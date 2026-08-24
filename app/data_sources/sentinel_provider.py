import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


class SentinelProvider:
    """
    Real Sentinel-2 provider for Copernicus Data Space Ecosystem.

    Workflow:
    1. Get OAuth access token
    2. Search real Sentinel-2 L2A scenes
    3. Filter/select lowest-cloud scene
    4. Use exact acquisition time
    5. Download a real True Color satellite image
    """

    def __init__(self) -> None:
        self.token_url = os.getenv(
            "CDSE_TOKEN_URL",
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        )

        self.stac_url = os.getenv(
            "CDSE_STAC_URL",
            "https://stac.dataspace.copernicus.eu/v1/search",
        )

        self.process_url = os.getenv(
            "CDSE_PROCESS_URL",
            "https://sh.dataspace.copernicus.eu/api/v1/process",
        )

        self.client_id = os.getenv("CDSE_CLIENT_ID")
        self.client_secret = os.getenv("CDSE_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "CDSE_CLIENT_ID and CDSE_CLIENT_SECRET are missing from .env"
            )

        self._access_token: str | None = None

    # =========================================================
    # AUTHENTICATION
    # =========================================================

    def get_access_token(self) -> str:
        if self._access_token:
            return self._access_token

        response = requests.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()
        token = data.get("access_token")

        if not token:
            raise RuntimeError(
                f"Access token not received: {data}"
            )

        self._access_token = token
        return token

    # =========================================================
    # SEARCH REAL SENTINEL-2 L2A PRODUCTS
    # =========================================================

    def search_sentinel2(
        self,
        bbox: list[float],
        limit: int = 20,
        lookback_days: int = 180,
        max_cloud_coverage: float = 80.0,
    ) -> list[dict[str, Any]]:

        if len(bbox) != 4:
            raise ValueError(
                "bbox must be [min_lon, min_lat, max_lon, max_lat]"
            )

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=lookback_days)

        payload = {
            "collections": ["sentinel-2-l2a"],
            "bbox": bbox,
            "datetime": (
                f"{start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}/"
                f"{end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            ),
            "limit": limit,
            "query": {
                "eo:cloud_cover": {
                    "lte": max_cloud_coverage
                }
            },
        }

        # Current STAC API search
        response = requests.post(
            self.stac_url,
            json=payload,
            timeout=60,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"STAC API error {response.status_code}: "
                f"{response.text}"
            )

        data = response.json()
        features = data.get("features", [])

        products: list[dict[str, Any]] = []

        for feature in features:
            products.append(
                {
                    "id": feature.get("id"),
                    "properties": feature.get("properties", {}),
                    "geometry": feature.get("geometry"),
                    "bbox": feature.get("bbox"),
                }
            )

        return products

    # =========================================================
    # CLOUD COVER
    # =========================================================

    @staticmethod
    def get_cloud_cover(
        product: dict[str, Any],
    ) -> float:

        value = product.get(
            "properties",
            {},
        ).get(
            "eo:cloud_cover",
            100.0,
        )

        try:
            return float(value)
        except (TypeError, ValueError):
            return 100.0

    # =========================================================
    # PRODUCT DATETIME
    # =========================================================

    @staticmethod
    def get_product_datetime(
        product: dict[str, Any],
    ) -> str | None:

        properties = product.get(
            "properties",
            {},
        )

        return (
            properties.get("datetime")
            or properties.get("start_datetime")
        )

    # =========================================================
    # SELECT BEST PRODUCT
    # =========================================================

    def get_best_sentinel2_product(
        self,
        bbox: list[float],
        lookback_days: int = 180,
        max_cloud_coverage: float = 80.0,
    ) -> dict[str, Any] | None:

        products = self.search_sentinel2(
            bbox=bbox,
            limit=100,
            lookback_days=lookback_days,
            max_cloud_coverage=max_cloud_coverage,
        )

        if not products:
            return None

        products.sort(
            key=self.get_cloud_cover
        )

        return products[0]

    # =========================================================
    # CREATE EXACT TIME RANGE
    # =========================================================

    @staticmethod
    def create_time_range(
        product_datetime: str,
        minutes_before: int = 30,
        minutes_after: int = 30,
    ) -> tuple[str, str]:

        dt = datetime.fromisoformat(
            product_datetime.replace("Z", "+00:00")
        )

        start_time = dt - timedelta(
            minutes=minutes_before
        )

        end_time = dt + timedelta(
            minutes=minutes_after
        )

        return (
            start_time.astimezone(
                timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            end_time.astimezone(
                timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    # =========================================================
    # DOWNLOAD REAL TRUE COLOR IMAGE
    # =========================================================

    def download_true_color_image(
        self,
        bbox: list[float],
        product_datetime: str,
        output_path: str = "data/best_sentinel2.png",
        width: int = 1024,
        height: int = 1024,
    ) -> str:

        token = self.get_access_token()

        start_time, end_time = self.create_time_range(
            product_datetime
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": {
                        "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                    },
                },
                "data": [
                    {
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": start_time,
                                "to": end_time,
                            },
                            "mosaickingOrder": "mostRecent",
                        },
                    }
                ],
            },
            "output": {
                "width": width,
                "height": height,
                "responses": [
                    {
                        "identifier": "default",
                        "format": {
                            "type": "image/png"
                        },
                    }
                ],
            },
            "evalscript": """
//VERSION=3

function setup() {
    return {
        input: [{
            bands: ["B02", "B03", "B04", "dataMask"],
            units: "REFLECTANCE"
        }],
        output: [{
            id: "default",
            bands: 3,
            sampleType: "AUTO"
        }]
    };
}

function evaluatePixel(sample) {
    if (sample.dataMask === 0) {
        return [0, 0, 0];
    }

    let r = Math.min(1, Math.max(0, sample.B04 * 2.5));
    let g = Math.min(1, Math.max(0, sample.B03 * 2.5));
    let b = Math.min(1, Math.max(0, sample.B02 * 2.5));

    r = Math.pow(r, 0.65);
    g = Math.pow(g, 0.65);
    b = Math.pow(b, 0.65);

    return [r, g, b];
}
""",
        }

        response = requests.post(
            self.process_url,
            headers=headers,
            json=payload,
            timeout=180,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Process API error {response.status_code}: "
                f"{response.text}"
            )

        output = Path(output_path)
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_bytes(response.content)

        if output.stat().st_size == 0:
            raise RuntimeError(
                "Downloaded image is empty."
            )

        return str(output)

    # =========================================================
    # COMPLETE REAL-DATA WORKFLOW
    # =========================================================

    def download_best_sentinel2_image(
        self,
        bbox: list[float],
        output_path: str = "data/best_sentinel2.png",
        lookback_days: int = 180,
        max_cloud_coverage: float = 80.0,
    ) -> dict[str, Any]:

        product = self.get_best_sentinel2_product(
            bbox=bbox,
            lookback_days=lookback_days,
            max_cloud_coverage=max_cloud_coverage,
        )

        if not product:
            raise RuntimeError(
                "No suitable Sentinel-2 products found."
            )

        product_datetime = self.get_product_datetime(
            product
        )

        if not product_datetime:
            raise RuntimeError(
                "Selected product has no acquisition datetime."
            )

        image_path = self.download_true_color_image(
            bbox=bbox,
            product_datetime=product_datetime,
            output_path=output_path,
        )

        return {
            "product_id": product.get("id"),
            "datetime": product_datetime,
            "cloud_cover": self.get_cloud_cover(product),
            "image_path": image_path,
            "product": product,
        }