from app.schemas.task import Task, TaskStatus
from app.tools.registry import ToolRegistry


class TaskExecutor:
    def __init__(self):
        self.registry = ToolRegistry()

    def execute_all(self, tasks: list[Task]) -> list[dict]:
        results = []

        for task in tasks:
            results.append(self.execute(task))

        return results

    def execute(self, task: Task) -> dict:
        try:
            tool = self.registry.get_tool(
                task.task_type.value
            )

            result = tool.run(task.parameters)

            task.status = TaskStatus.COMPLETED

            return {
                "task_id": task.task_id,
                "task_type": task.task_type.value,
                "status": "completed",
                "result": result,
            }

        except Exception as error:
            task.status = TaskStatus.FAILED

            return {
                "task_id": task.task_id,
                "task_type": task.task_type.value,
                "status": "failed",
                "error": str(error),
            }