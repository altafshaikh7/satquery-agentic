import os
from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


class SentinelProvider:
    """
    Real Copernicus Data Space Ecosystem provider.

    Features:
    - OAuth2 authentication
    - Real Sentinel-2 catalog search
    - Real satellite product metadata retrieval
    """

    def __init__(self) -> None:
        self.client_id = os.getenv("CDSE_CLIENT_ID")
        self.client_secret = os.getenv("CDSE_CLIENT_SECRET")

        self.token_url = os.getenv(
            "CDSE_TOKEN_URL",
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        )

        self.catalog_url = os.getenv(
            "CDSE_CATALOG_URL",
            "https://sh.dataspace.copernicus.eu/catalog/v1/search",
        )

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "CDSE_CLIENT_ID and CDSE_CLIENT_SECRET are required. "
                "Add them to the .env file."
            )

    def get_access_token(self) -> str:
        response = requests.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30,
        )

        response.raise_for_status()

        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise RuntimeError(
                f"CDSE authentication failed. Response: {token_data}"
            )

        return access_token

    def search_sentinel2(
        self,
        bbox: list[float],
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 10,
        max_cloud_cover: float = 30,
    ) -> list[dict[str, Any]]:
        """
        Search real Sentinel-2 imagery.

        bbox format:
        [min_longitude, min_latitude, max_longitude, max_latitude]

        Example:
        [73.80, 16.70, 73.90, 16.80]
        """

        if len(bbox) != 4:
            raise ValueError(
                "bbox must contain 4 values: "
                "[min_lon, min_lat, max_lon, max_lat]"
            )

        if start_date is None:
            start_date = (
                datetime.now(timezone.utc) - timedelta(days=30)
            ).strftime("%Y-%m-%dT00:00:00Z")

        if end_date is None:
            end_date = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT23:59:59Z"
            )

        token = self.get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "collections": ["sentinel-2-l2a"],
            "bbox": bbox,
            "datetime": f"{start_date}/{end_date}",
            "limit": limit,
            "filter": (
                f"eo:cloud_cover < {max_cloud_cover}"
            ),
            "filter-lang": "cql2-text",
        }

        response = requests.post(
            self.catalog_url,
            headers=headers,
            json=payload,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()
        return data.get("features", [])

    def get_latest_sentinel2(
        self,
        bbox: list[float],
        max_cloud_cover: float = 30,
    ) -> dict[str, Any] | None:
        """
        Return the latest real Sentinel-2 product.
        """

        features = self.search_sentinel2(
            bbox=bbox,
            limit=20,
            max_cloud_cover=max_cloud_cover,
        )

        if not features:
            return None

        features.sort(
            key=lambda item: item.get(
                "properties", {}
            ).get("datetime", ""),
            reverse=True,
        )

        return features[0]