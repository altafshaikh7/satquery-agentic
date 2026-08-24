class GeospatialValidator:
    def validate(self, latitude: float, longitude: float) -> bool:
        return (
            -90 <= latitude <= 90
            and -180 <= longitude <= 180
        )