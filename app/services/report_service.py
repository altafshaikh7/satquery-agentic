class ReportService:
    def generate(self, result: dict) -> dict:
        return {
            "status": "success",
            "report": result,
        }