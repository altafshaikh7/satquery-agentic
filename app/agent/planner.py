from app.agent.router import QueryRouter
from app.schemas.query import QueryRequest
from app.schemas.task import Task


class TaskPlanner:
    """
    Converts a user query into an executable task plan.
    """

    def __init__(self):
        self.router = QueryRouter()

    def create_plan(self, request: QueryRequest) -> list[Task]:
        tool_name = self.router.route(request)

        task = Task(
            task_id="task_1",
            task_type=tool_name,
            description=f"Execute {tool_name} for the given remote sensing query",
            status="pending",
            input_data={
                "query": request.query,
            },
        )

        return [task]