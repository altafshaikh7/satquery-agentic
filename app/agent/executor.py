from typing import Any

from app.schemas.task import Task, TaskStatus
from app.tools.registry import ToolRegistry


class TaskExecutor:
    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or ToolRegistry()

    def execute(self, task: Task) -> dict[str, Any]:
        try:
            task.status = TaskStatus.RUNNING

            result = self.registry.execute(
                task_type=task.task_type,
                parameters=task.parameters,
            )

            task.status = TaskStatus.COMPLETED

            return {
                "task_id": task.task_id,
                "task_type": task.task_type.value,
                "status": task.status.value,
                "result": result,
            }

        except Exception as error:
            task.status = TaskStatus.FAILED

            return {
                "task_id": task.task_id,
                "task_type": task.task_type.value,
                "status": task.status.value,
                "error": str(error),
            }

    def execute_all(self, tasks: list[Task]) -> list[dict[str, Any]]:
        return [self.execute(task) for task in tasks]