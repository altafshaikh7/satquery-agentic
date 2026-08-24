from app.agent.executor import TaskExecutor
from app.agent.planner import TaskPlanner
from app.agent.router import QueryRouter
from app.agent.synthesizer import ResponseSynthesizer
from app.agent.verifier import ResultVerifier
from app.schemas.query import QueryRequest


class AgentGraph:
    def __init__(self):
        self.router = QueryRouter()
        self.planner = TaskPlanner()
        self.executor = TaskExecutor()
        self.verifier = ResultVerifier()
        self.synthesizer = ResponseSynthesizer()

    def run(self, request: QueryRequest) -> dict:
        route = self.router.route(request)

        tasks = self.planner.create_plan(request)

        results = self.executor.execute_all(tasks)

        verification = self.verifier.verify(results)

        answer = self.synthesizer.synthesize(
            query=request.query,
            route=route,
            results=results,
            verification=verification,
        )

        return {
            "query": request.query,
            "route": route,
            "tasks": [
                task.model_dump(mode="json")
                for task in tasks
            ],
            "results": results,
            "answer": answer,
            "confidence": verification["confidence"],
        }