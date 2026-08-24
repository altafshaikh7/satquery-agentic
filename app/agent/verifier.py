class ResultVerifier:
    def verify(self, results: list[dict]) -> dict:
        successful_results = [
            result
            for result in results
            if result.get("status") == "completed"
        ]

        confidence = 0.0

        if successful_results:
            confidence = round(
                len(successful_results) / len(results),
                2,
            )

        return {
            "verified": len(successful_results) > 0,
            "confidence": confidence,
            "successful_tasks": len(successful_results),
            "total_tasks": len(results),
        }