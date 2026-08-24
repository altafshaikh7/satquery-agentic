from app.schemas.query import QueryRequest
from app.schemas.task import Task, TaskStatus, TaskType


class TaskPlanner:
    def create_plan(self, request: QueryRequest) -> list[Task]:
        task_type = self._get_task_type(request.query)

        task = Task(
            task_id="task_1",
            task_type=task_type,
            description=(
                f"Execute {task_type.value} "
                "for the given remote sensing query"
            ),
            status=TaskStatus.PENDING,
            dependencies=[],
            parameters={
                "query": request.query,
                "image_urls": request.image_urls,
            },
        )

        return [task]

    def _get_task_type(self, query: str) -> TaskType:
        query_lower = query.lower()

        if any(
            word in query_lower
            for word in ["change", "compare", "difference"]
        ):
            return TaskType.CHANGE_ANALYSIS

        if any(
            word in query_lower
            for word in ["caption", "describe", "scene"]
        ):
            return TaskType.SCENE_CAPTION

        return TaskType.SINGLE_IMAGE_VQA