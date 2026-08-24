from typing import Any


class ConfidenceEstimator:

    def estimate(
        self,
        result: dict[str, Any],
    ) -> float:

        if result.get("status") != "success":
            return 0.0

        confidence = 0.60

        # Successful tool execution
        confidence += 0.10

        # Real Sentinel metadata available
        if result.get("sentinel"):
            confidence += 0.10

        # Change analysis evidence
        if result.get("tool") == "change_analysis":

            if result.get("change_percentage") is not None:
                confidence += 0.05

            if result.get("ndvi_analysis"):
                confidence += 0.10

        # Vision analysis
        if result.get("caption") or result.get("answer"):
            confidence += 0.05

        return round(
            min(confidence, 1.0),
            2,
        )