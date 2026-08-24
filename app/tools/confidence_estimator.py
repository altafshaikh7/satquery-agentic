class ConfidenceEstimator:
    def estimate(self, result: dict) -> float:
        if result.get("status") == "success":
            return 0.85

        return 0.0