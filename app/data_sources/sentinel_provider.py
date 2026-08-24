import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import requests
from dotenv import load_dotenv
from PIL import Image

load_dotenv()


class SentinelProvider:
    """
    Sentinel-2 provider for Copernicus Data Space Ecosystem.

    Features:
    - OAuth authentication
    - Sentinel-2 L2A STAC search
    - Low-cloud scene selection
    - Scene selection near target date
    - True-color RGB download
    - Red + NIR + dataMask TIFF download
    - NDVI calculation
    """

    def __init__(self) -> None:
        self.token_url = os.getenv(
            "CDSE_TOKEN_URL",
            "https://identity.dataspace.copernicus.eu/"
            "auth/realms/CDSE/protocol/openid-connect/token",
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
                "CDSE_CLIENT_ID and CDSE_CLIENT_SECRET "
                "are missing from your .env file."
            )

        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    # =========================================================
    # AUTHENTICATION
    # =========================================================

    def get_access_token(self) -> str:
        """
        Get or refresh OAuth access token.
        """

        current_time = time.time()

        if (
            self._access_token
            and current_time < self._token_expires_at
        ):
            return self._access_token

        print("Authenticating with Copernicus Data Space...")

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

        expires_in = int(
            data.get("expires_in", 300)
        )

        self._access_token = token

        # Refresh 30 seconds before expiry.
        self._token_expires_at = (
            time.time()
            + max(expires_in - 30, 30)
        )

        return token

    # =========================================================
    # DATETIME PARSING
    # =========================================================

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        """
        Parse ISO date/datetime into UTC.
        """

        try:
            dt = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError as error:
            raise ValueError(
                "Invalid date format. Use for example "
                "2025-01-01 or 2025-01-01T10:30:00Z"
            ) from error

        if dt.tzinfo is None:
            dt = dt.replace(
                tzinfo=timezone.utc
            )

        return dt.astimezone(
            timezone.utc
        )

    # =========================================================
    # BBOX VALIDATION
    # =========================================================

    @staticmethod
    def _validate_bbox(
        bbox: list[float],
    ) -> None:
        if (
            not isinstance(bbox, list)
            or len(bbox) != 4
        ):
            raise ValueError(
                "bbox must be "
                "[min_lon, min_lat, max_lon, max_lat]"
            )

        try:
            min_lon, min_lat, max_lon, max_lat = (
                map(float, bbox)
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "bbox values must be numbers."
            ) from error

        if min_lon >= max_lon:
            raise ValueError(
                "bbox min_lon must be less than max_lon."
            )

        if min_lat >= max_lat:
            raise ValueError(
                "bbox min_lat must be less than max_lat."
            )

        if not (
            -180 <= min_lon <= 180
            and -180 <= max_lon <= 180
            and -90 <= min_lat <= 90
            and -90 <= max_lat <= 90
        ):
            raise ValueError(
                "bbox coordinates are outside valid "
                "longitude/latitude ranges."
            )

    # =========================================================
    # SEARCH SENTINEL-2 BY DATE RANGE
    # =========================================================

    def search_sentinel2_by_date_range(
        self,
        bbox: list[float],
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        max_cloud_coverage: float = 80.0,
    ) -> list[dict[str, Any]]:
        """
        Search Sentinel-2 L2A scenes using STAC.
        """

        self._validate_bbox(bbox)

        if start_date.tzinfo is None:
            start_date = start_date.replace(
                tzinfo=timezone.utc
            )

        if end_date.tzinfo is None:
            end_date = end_date.replace(
                tzinfo=timezone.utc
            )

        start_date = start_date.astimezone(
            timezone.utc
        )

        end_date = end_date.astimezone(
            timezone.utc
        )

        if start_date > end_date:
            raise ValueError(
                "start_date must be earlier than end_date."
            )

        payload = {
            "collections": [
                "sentinel-2-l2a"
            ],
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

        print(
            "Searching Sentinel-2 scenes from "
            f"{start_date.date()} to {end_date.date()}..."
        )

        response = requests.post(
            self.stac_url,
            json=payload,
            timeout=60,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"STAC API error "
                f"{response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        features = data.get(
            "features",
            [],
        )

        products: list[dict[str, Any]] = []

        for feature in features:
            products.append(
                {
                    "id": feature.get("id"),
                    "properties": feature.get(
                        "properties",
                        {},
                    ),
                    "geometry": feature.get(
                        "geometry"
                    ),
                    "bbox": feature.get("bbox"),
                }
            )

        print(
            f"Found {len(products)} Sentinel-2 scenes."
        )

        return products

    # =========================================================
    # SEARCH RECENT SENTINEL-2
    # =========================================================

    def search_sentinel2(
        self,
        bbox: list[float],
        limit: int = 20,
        lookback_days: int = 180,
        max_cloud_coverage: float = 80.0,
    ) -> list[dict[str, Any]]:
        """
        Search recent Sentinel-2 scenes.
        """

        end_date = datetime.now(
            timezone.utc
        )

        start_date = (
            end_date
            - timedelta(days=lookback_days)
        )

        return self.search_sentinel2_by_date_range(
            bbox=bbox,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            max_cloud_coverage=max_cloud_coverage,
        )

    # =========================================================
    # CLOUD COVER
    # =========================================================

    @staticmethod
    def get_cloud_cover(
        product: dict[str, Any],
    ) -> float:
        value = (
            product.get(
                "properties",
                {},
            ).get(
                "eo:cloud_cover",
                100.0,
            )
        )

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
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
    # BEST RECENT PRODUCT
    # =========================================================

    def get_best_sentinel2_product(
        self,
        bbox: list[float],
        lookback_days: int = 180,
        max_cloud_coverage: float = 80.0,
    ) -> dict[str, Any] | None:
        """
        Select lowest-cloud recent scene.
        """

        products = self.search_sentinel2(
            bbox=bbox,
            limit=100,
            lookback_days=lookback_days,
            max_cloud_coverage=max_cloud_coverage,
        )

        if not products:
            return None

        products.sort(
            key=lambda product: (
                self.get_cloud_cover(product),
                self.get_product_datetime(product)
                or "",
            )
        )

        return products[0]

    # =========================================================
    # BEST PRODUCT NEAR TARGET DATE
    # =========================================================

    def get_best_product_for_date(
        self,
        bbox: list[float],
        target_date: str,
        search_window_days: int = 30,
        max_cloud_coverage: float = 80.0,
    ) -> dict[str, Any] | None:
        """
        Find best low-cloud scene near a target date.

        Priority:
        1. Lower cloud cover
        2. Closer acquisition date
        """

        self._validate_bbox(bbox)

        target_datetime = (
            self._parse_datetime(target_date)
        )

        start_date = (
            target_datetime
            - timedelta(days=search_window_days)
        )

        end_date = (
            target_datetime
            + timedelta(days=search_window_days)
        )

        products = (
            self.search_sentinel2_by_date_range(
                bbox=bbox,
                start_date=start_date,
                end_date=end_date,
                limit=100,
                max_cloud_coverage=max_cloud_coverage,
            )
        )

        if not products:
            return None

        def sort_key(
            product: dict[str, Any],
        ) -> tuple[float, float]:

            cloud_cover = self.get_cloud_cover(
                product
            )

            product_datetime = (
                self.get_product_datetime(product)
            )

            if not product_datetime:
                return (
                    cloud_cover,
                    float("inf"),
                )

            try:
                dt = self._parse_datetime(
                    product_datetime
                )

                difference = abs(
                    (
                        dt
                        - target_datetime
                    ).total_seconds()
                )

            except ValueError:
                difference = float("inf")

            return (
                cloud_cover,
                difference,
            )

        products.sort(
            key=sort_key
        )

        best_product = products[0]

        print(
            "Selected scene: "
            f"{best_product.get('id')} | "
            f"Cloud: "
            f"{self.get_cloud_cover(best_product):.2f}% | "
            f"Date: "
            f"{self.get_product_datetime(best_product)}"
        )

        return best_product

    # =========================================================
    # EXACT TIME RANGE
    # =========================================================

    @staticmethod
    def create_time_range(
        product_datetime: str,
        minutes_before: int = 30,
        minutes_after: int = 30,
    ) -> tuple[str, str]:
        """
        Create a narrow Process API time range.
        """

        dt = SentinelProvider._parse_datetime(
            product_datetime
        )

        start_time = (
            dt
            - timedelta(minutes=minutes_before)
        )

        end_time = (
            dt
            + timedelta(minutes=minutes_after)
        )

        return (
            start_time.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            end_time.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        )

    # =========================================================
    # PROCESS API HEADERS
    # =========================================================

    def _get_process_headers(
        self,
    ) -> dict[str, str]:

        token = self.get_access_token()

        return {
            "Authorization": (
                f"Bearer {token}"
            ),
            "Content-Type": (
                "application/json"
            ),
        }

    # =========================================================
    # DOWNLOAD TRUE COLOR IMAGE
    # =========================================================

    def download_true_color_image(
        self,
        bbox: list[float],
        product_datetime: str,
        output_path: str,
        width: int = 512,
        height: int = 512,
    ) -> str:
        """
        Download RGB image for a known acquisition datetime.
        """

        self._validate_bbox(bbox)

        start_time, end_time = (
            self.create_time_range(
                product_datetime
            )
        )

        headers = (
            self._get_process_headers()
        )

        payload = {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": {
                        "crs": (
                            "http://www.opengis.net/"
                            "def/crs/EPSG/0/4326"
                        )
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
                            "mosaickingOrder": (
                                "mostRecent"
                            ),
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
            bands: [
                "B02",
                "B03",
                "B04",
                "dataMask"
            ],
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

        print(
            f"Downloading RGB image: {output_path}"
        )

        response = requests.post(
            self.process_url,
            headers=headers,
            json=payload,
            timeout=180,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Process API error "
                f"{response.status_code}: "
                f"{response.text}"
            )

        output = Path(output_path)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_bytes(
            response.content
        )

        if output.stat().st_size == 0:
            raise RuntimeError(
                "Downloaded RGB image is empty."
            )

        # Validate the image immediately.
        try:
            with Image.open(output) as image:
                image.verify()
        except Exception as error:
            if output.exists():
                output.unlink()

            raise RuntimeError(
                f"Downloaded file is not a valid image: {error}"
            ) from error

        return str(output)

    # =========================================================
    # DOWNLOAD NDVI SOURCE DATA
    # =========================================================

    def download_ndvi_data(
        self,
        bbox: list[float],
        product_datetime: str,
        output_path: str,
        width: int = 512,
        height: int = 512,
    ) -> str:
        """
        Download Red, NIR and dataMask as FLOAT32 TIFF.
        """

        self._validate_bbox(bbox)

        start_time, end_time = (
            self.create_time_range(
                product_datetime
            )
        )

        headers = (
            self._get_process_headers()
        )

        payload = {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": {
                        "crs": (
                            "http://www.opengis.net/"
                            "def/crs/EPSG/0/4326"
                        )
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
                            "mosaickingOrder": (
                                "mostRecent"
                            ),
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
                            "type": "image/tiff"
                        },
                    }
                ],
            },
            "evalscript": """
//VERSION=3

function setup() {
    return {
        input: [{
            bands: [
                "B04",
                "B08",
                "dataMask"
            ],
            units: "REFLECTANCE"
        }],
        output: [{
            id: "default",
            bands: 3,
            sampleType: "FLOAT32"
        }]
    };
}

function evaluatePixel(sample) {
    return [
        sample.B04,
        sample.B08,
        sample.dataMask
    ];
}
""",
        }

        print(
            f"Downloading NDVI source data: "
            f"{output_path}"
        )

        response = requests.post(
            self.process_url,
            headers=headers,
            json=payload,
            timeout=180,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"NDVI Process API error "
                f"{response.status_code}: "
                f"{response.text}"
            )

        output = Path(output_path)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_bytes(
            response.content
        )

        if output.stat().st_size == 0:
            raise RuntimeError(
                "Downloaded NDVI TIFF is empty."
            )

        return str(output)

    # =========================================================
    # LOAD NDVI DATA
    # =========================================================

    @staticmethod
    def load_ndvi_data(
        image_path: str,
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]:
        """
        Load TIFF bands:
        - Red
        - NIR
        - dataMask
        """

        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"NDVI data file not found: "
                f"{image_path}"
            )

        with Image.open(path) as image:
            data = np.array(
                image,
                dtype=np.float32,
            )

        if (
            data.ndim != 3
            or data.shape[-1] < 3
        ):
            raise RuntimeError(
                "Invalid NDVI TIFF. Expected "
                "Red, NIR and dataMask bands."
            )

        red = data[:, :, 0]
        nir = data[:, :, 1]
        data_mask = data[:, :, 2]

        return (
            red,
            nir,
            data_mask,
        )

    # =========================================================
    # CALCULATE NDVI
    # =========================================================

    @staticmethod
    def calculate_ndvi(
        red: np.ndarray,
        nir: np.ndarray,
        data_mask: np.ndarray | None = None,
    ) -> np.ndarray:
        """
        NDVI = (NIR - RED) / (NIR + RED)
        """

        red = red.astype(
            np.float32
        )

        nir = nir.astype(
            np.float32
        )

        denominator = nir + red

        ndvi = np.full(
            red.shape,
            np.nan,
            dtype=np.float32,
        )

        valid = (
            np.isfinite(red)
            & np.isfinite(nir)
            & (denominator > 0.00001)
        )

        if data_mask is not None:
            valid = (
                valid
                & np.isfinite(data_mask)
                & (data_mask > 0)
            )

        ndvi[valid] = (
            (nir[valid] - red[valid])
            / denominator[valid]
        )

        return np.clip(
            ndvi,
            -1.0,
            1.0,
        )

    # =========================================================
    # DOWNLOAD RGB FOR SPECIFIC DATE
    # =========================================================

    def download_sentinel2_image_for_date(
        self,
        bbox: list[float],
        target_date: str,
        output_path: str,
        search_window_days: int = 30,
        max_cloud_coverage: float = 80.0,
    ) -> dict[str, Any]:
        """
        Find the best scene near target_date
        and download its true-color image.
        """

        product = self.get_best_product_for_date(
            bbox=bbox,
            target_date=target_date,
            search_window_days=search_window_days,
            max_cloud_coverage=max_cloud_coverage,
        )

        if not product:
            raise RuntimeError(
                "No suitable Sentinel-2 product found "
                f"near {target_date}."
            )

        product_datetime = (
            self.get_product_datetime(product)
        )

        if not product_datetime:
            raise RuntimeError(
                "Selected product has no "
                "acquisition datetime."
            )

        image_path = (
            self.download_true_color_image(
                bbox=bbox,
                product_datetime=product_datetime,
                output_path=output_path,
            )
        )

        return {
            "product_id": product.get("id"),
            "datetime": product_datetime,
            "cloud_cover": (
                self.get_cloud_cover(product)
            ),
            "image_path": image_path,
            "product": product,
        }

    # =========================================================
    # DOWNLOAD NDVI FOR SPECIFIC DATE
    # =========================================================

    def download_ndvi_for_date(
        self,
        bbox: list[float],
        target_date: str,
        output_path: str,
        search_window_days: int = 30,
        max_cloud_coverage: float = 30.0,
    ) -> dict[str, Any]:
        """
        Find best low-cloud scene near target_date,
        download TIFF and calculate NDVI.
        """

        product = self.get_best_product_for_date(
            bbox=bbox,
            target_date=target_date,
            search_window_days=search_window_days,
            max_cloud_coverage=max_cloud_coverage,
        )

        if not product:
            raise RuntimeError(
                "No suitable low-cloud Sentinel-2 product "
                f"found near {target_date}."
            )

        product_datetime = (
            self.get_product_datetime(product)
        )

        if not product_datetime:
            raise RuntimeError(
                "Selected product has no "
                "acquisition datetime."
            )

        ndvi_data_path = (
            self.download_ndvi_data(
                bbox=bbox,
                product_datetime=product_datetime,
                output_path=output_path,
            )
        )

        return {
            "product_id": product.get("id"),
            "datetime": product_datetime,
            "cloud_cover": (
                self.get_cloud_cover(product)
            ),
            "ndvi_data_path": ndvi_data_path,
            "product": product,
        }

    # =========================================================
    # DOWNLOAD BEST RECENT IMAGE
    # =========================================================

    def download_best_sentinel2_image(
        self,
        bbox: list[float],
        output_path: str = (
            "data/best_sentinel2.png"
        ),
        lookback_days: int = 180,
        max_cloud_coverage: float = 80.0,
    ) -> dict[str, Any]:

        product = (
            self.get_best_sentinel2_product(
                bbox=bbox,
                lookback_days=lookback_days,
                max_cloud_coverage=max_cloud_coverage,
            )
        )

        if not product:
            raise RuntimeError(
                "No suitable Sentinel-2 products found."
            )

        product_datetime = (
            self.get_product_datetime(product)
        )

        if not product_datetime:
            raise RuntimeError(
                "Selected product has no "
                "acquisition datetime."
            )

        image_path = (
            self.download_true_color_image(
                bbox=bbox,
                product_datetime=product_datetime,
                output_path=output_path,
            )
        )

        return {
            "product_id": product.get("id"),
            "datetime": product_datetime,
            "cloud_cover": (
                self.get_cloud_cover(product)
            ),
            "image_path": image_path,
            "product": product,
        }