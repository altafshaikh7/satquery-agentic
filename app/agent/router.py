from app.schemas.query import QueryRequest


class QueryRouter:
    """
    Routes a remote-sensing query to the most suitable analysis tool.
    """

    ROUTES = {
        "change_analysis": [
            "change",
            "changed",
            "difference",
            "compare",
            "before",
            "after",
            "construction",
            "deforestation",
            "urban expansion",
            "growth",
        ],
        "single_image_vqa": [
            "what is",
            "what are",
            "how many",
            "identify",
            "detect",
            "is there",
            "are there",
        ],
        "scene_caption": [
            "describe",
            "caption",
            "scene",
            "overview",
            "summarize image",
        ],
        "optical_sar_fusion": [
            "sar",
            "radar",
            "optical",
            "fusion",
            "sentinel-1",
            "sentinel-2",
        ],
        "geospatial_validator": [
            "location",
            "coordinates",
            "latitude",
            "longitude",
            "where",
            "geo",
            "geospatial",
        ],
        "metadata_validator": [
            "metadata",
            "acquisition date",
            "sensor",
            "resolution",
            "cloud cover",
        ],
        "text_grounding": [
            "find",
            "locate",
            "show me",
            "highlight",
            "where is",
        ],
    }

    def route(self, request: QueryRequest) -> str:
        """
        Determine which tool should handle the user query.
        """
        query = request.query.lower().strip()

        for route_name, keywords in self.ROUTES.items():
            for keyword in keywords:
                if keyword in query:
                    return route_name

        return "single_image_vqa"