from app.schemas.query import QueryRequest
from app.schemas.task import TaskType


class QueryRouter:
    def route(self, request: QueryRequest) -> str:
        query = request.query.lower()

        if any(
            word in query
            for word in ["change", "compare", "difference"]
        ):
            return TaskType.CHANGE_ANALYSIS.value

        if any(
            word in query
            for word in ["caption", "describe", "scene"]
        ):
            return TaskType.SCENE_CAPTION.value

        return TaskType.SINGLE_IMAGE_VQA.value