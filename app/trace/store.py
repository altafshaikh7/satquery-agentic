class TraceStore:
    def __init__(self):
        self._traces: dict[str, dict] = {}

    def save(self, trace_id: str, trace: dict):
        self._traces[trace_id] = trace

    def get(self, trace_id: str):
        return self._traces.get(trace_id)

    def list_all(self) -> list[dict]:
        return list(self._traces.values())