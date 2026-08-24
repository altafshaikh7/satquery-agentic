from concurrent.futures import ThreadPoolExecutor, as_completed

from app.schemas.task import Task, TaskStatus
from app.tools.registry import ToolRegistry


class TaskExecutor:
    def __init__(self):
        self.registry = ToolRegistry()

    def execute_all(
        self,
        tasks: list[Task],
    ) -> list[dict]:

        results: list[dict] = []

        completed_task_ids: set[str] = set()

        results_by_task_id: dict[str, dict] = {}

        remaining_tasks = list(tasks)

        while remaining_tasks:

            ready_tasks = [
                task
                for task in remaining_tasks
                if all(
                    dependency in completed_task_ids
                    for dependency in task.dependencies
                )
            ]

            # ---------------------------------------------
            # NO TASK CAN PROCEED
            # ---------------------------------------------

            if not ready_tasks:

                for task in remaining_tasks:

                    task.status = TaskStatus.FAILED

                    results.append(
                        {
                            "task_id": task.task_id,
                            "task_type": (
                                task.task_type.value
                            ),
                            "status": "failed",
                            "error": (
                                "Task dependencies could "
                                "not be satisfied."
                            ),
                        }
                    )

                break

            # ---------------------------------------------
            # PASS DEPENDENCY RESULTS TO READY TASKS
            # ---------------------------------------------

            for task in ready_tasks:

                dependency_results = {}

                for dependency_id in task.dependencies:

                    dependency_result = (
                        results_by_task_id.get(
                            dependency_id
                        )
                    )

                    if dependency_result is not None:

                        dependency_results[
                            dependency_id
                        ] = dependency_result

                if dependency_results:

                    task.parameters[
                        "dependency_results"
                    ] = dependency_results

            # ---------------------------------------------
            # EXECUTE READY TASKS IN PARALLEL
            # ---------------------------------------------

            with ThreadPoolExecutor(
                max_workers=len(ready_tasks)
            ) as executor:

                future_to_task = {
                    executor.submit(
                        self.execute,
                        task,
                    ): task
                    for task in ready_tasks
                }

                for future in as_completed(
                    future_to_task
                ):

                    task = future_to_task[future]

                    result = future.result()

                    results.append(result)

                    results_by_task_id[
                        task.task_id
                    ] = result

                    if (
                        result["status"]
                        == "completed"
                    ):

                        completed_task_ids.add(
                            task.task_id
                        )

            # ---------------------------------------------
            # REMOVE EXECUTED TASKS
            # ---------------------------------------------

            remaining_tasks = [
                task
                for task in remaining_tasks
                if task not in ready_tasks
            ]

        return results

    def execute(
        self,
        task: Task,
    ) -> dict:

        try:

            tool = self.registry.get_tool(
                task.task_type.value
            )

            result = tool.run(
                task.parameters
            )

            task.status = TaskStatus.COMPLETED

            return {
                "task_id": task.task_id,
                "task_type": (
                    task.task_type.value
                ),
                "status": "completed",
                "result": result,
            }

        except Exception as error:

            task.status = TaskStatus.FAILED

            return {
                "task_id": task.task_id,
                "task_type": (
                    task.task_type.value
                ),
                "status": "failed",
                "error": str(error),
            }