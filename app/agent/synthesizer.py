class ResponseSynthesizer:
    def synthesize(
        self,
        query: str,
        route: str,
        results: list[dict],
        verification: dict,
    ) -> str:

        successful_results = [
            result
            for result in results
            if result.get("status") == "completed"
        ]

        if not successful_results:
            errors = [
                result.get("error", "Unknown error")
                for result in results
            ]

            return (
                "Unable to complete the remote sensing analysis. "
                + " | ".join(errors)
            )

        first_result = successful_results[0].get(
            "result",
            {},
        )

        if route == "change_analysis":
            percentage = first_result.get(
                "change_percentage",
                0,
            )

            return (
                f"Change analysis completed. "
                f"Detected change across approximately "
                f"{percentage}% of the analyzed pixels."
            )

        if route == "scene_caption":
            return first_result.get(
                "caption",
                "Scene analysis completed.",
            )

        return first_result.get(
            "answer",
            "Image analysis completed.",
        )