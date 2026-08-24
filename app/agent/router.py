from app.schemas.query import QueryRequest
from app.schemas.task import TaskType


class QueryRouter:
    def route(self, request: QueryRequest) -> str:
        query = request.query.lower()

        if any(
            word in query
            for word in [
                "change",
                "compare",
                "difference",
                "changed",
                "change detection",
            ]
        ):
            return TaskType.CHANGE_ANALYSIS.value

        if any(
            word in query
            for word in [
                "caption",
                "describe",
                "scene",
                "analyze",
                "analyse",
                "land use",
                "land cover",
                "water body",
                "water bodies",
                "vegetation",
                "forest",
                "agriculture",
                "agricultural",
                "urban",
                "built-up",
                "satellite image",
                "remote sensing",
            ]
        ):
            return TaskType.SCENE_CAPTION.value

        return TaskType.SINGLE_IMAGE_VQA.value