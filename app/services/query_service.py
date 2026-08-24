from app.agent.graph import AgentGraph
from app.schemas.query import QueryRequest
from app.schemas.response import QueryResponse


class QueryService:
    def __init__(self):
        self.agent = AgentGraph()

    def process(
        self,
        request: QueryRequest,
    ) -> QueryResponse:

        result = self.agent.run(request)

        return QueryResponse(
            query=result["query"],
            route=result["route"],
            tasks=result["tasks"],
            results=result["results"],
            answer=result["answer"],
            confidence=result["confidence"],
        )