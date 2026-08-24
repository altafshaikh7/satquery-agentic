import uuid

from app.trace.store import TraceStore


class TraceRecorder:
    def __init__(self, store: TraceStore):
        self.store = store

    def record(
        self,
        query: str,
        route: str,
        steps: list[dict],
    ) -> str:

        trace_id = str(uuid.uuid4())

        trace = {
            "trace_id": trace_id,
            "query": query,
            "route": route,
            "steps": steps,
        }

        self.store.save(trace_id, trace)

        return trace_id