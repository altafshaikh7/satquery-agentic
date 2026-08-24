class GeospatialValidator:

    def validate(
        self,
        latitude: float,
        longitude: float,
    ) -> bool:

        return (
            -90 <= latitude <= 90
            and -180 <= longitude <= 180
        )

    def validate_bbox(
        self,
        bbox: list[float],
    ) -> bool:

        if not isinstance(bbox, list):
            return False

        if len(bbox) != 4:
            return False

        min_lon, min_lat, max_lon, max_lat = bbox

        if not all(
            isinstance(value, (int, float))
            for value in bbox
        ):
            return False

        if not (
            -180 <= min_lon <= 180
            and -180 <= max_lon <= 180
        ):
            return False

        if not (
            -90 <= min_lat <= 90
            and -90 <= max_lat <= 90
        ):
            return False

        if min_lon >= max_lon:
            return False

        if min_lat >= max_lat:
            return False

        return True