from app.schemas.query import QueryRequest
from app.schemas.task import Task, TaskStatus, TaskType


class TaskPlanner:
    def create_plan(self, request: QueryRequest) -> list[Task]:
        task_type = self._get_task_type(request.query)

        parameters = {
            "query": request.query,
            "question": request.query,
            "image_urls": request.image_urls,
        }

        if request.bbox is not None:
            parameters["bbox"] = request.bbox

        task = Task(
            task_id="task_1",
            task_type=task_type,
            description=(
                f"Execute {task_type.value} "
                "for the given remote sensing query"
            ),
            status=TaskStatus.PENDING,
            dependencies=[],
            parameters=parameters,
        )

        return [task]

    def _get_task_type(self, query: str) -> TaskType:
        query_lower = query.lower()

        if any(
            word in query_lower
            for word in [
                "change",
                "compare",
                "difference",
            ]
        ):
            return TaskType.CHANGE_ANALYSIS

        if any(
            word in query_lower
            for word in [
                "caption",
                "describe",
                "scene",
                "analyze",
                "analyse",
                "land use",
                "vegetation",
                "water bodies",
                "water body",
                "infrastructure",
            ]
        ):
            return TaskType.SCENE_CAPTION

        # If bbox is provided, default to scene analysis
        if request.bbox is not None:
            return TaskType.SCENE_CAPTION

        return TaskType.SINGLE_IMAGE_VQA