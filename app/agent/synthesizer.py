import json

from app.llm.provider import get_llm_provider


class ResponseSynthesizer:
    def __init__(self):
        self.llm = get_llm_provider()

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

        analysis_results = [
            result.get("result", {})
            for result in successful_results
        ]

        prompt = f"""
You are SatQuery AI, an expert remote sensing and Earth Observation
analysis assistant.

Generate a clear, accurate final answer based ONLY on the verified
analysis results provided below.

USER QUERY:
{query}

ANALYSIS ROUTE:
{route}

TOOL RESULTS:
{json.dumps(analysis_results, indent=2, default=str)}

VERIFICATION RESULT:
{json.dumps(verification, indent=2, default=str)}

INSTRUCTIONS:

1. Answer the user's original question directly first.

2. Use only information supported by the provided tool results.
Do not invent satellite observations, locations, dates, or conclusions.

3. If the route is "change_analysis":
   - Report whether change was detected.
   - Mention change percentage.
   - Mention the before and after Sentinel-2 acquisition dates.
   - Include NDVI before and after when available.
   - Explain whether vegetation gain or vegetation loss was detected.
   - Clearly distinguish pixel-level change from vegetation change.

4. If the route is "scene_caption":
   - Provide a structured Earth Observation description.
   - Mention only land cover, water, vegetation, infrastructure, or
     other features actually supported by the tool result.

5. If the route is "single_image_vqa":
   - Give a direct answer first.
   - Then provide a short evidence-based explanation.

6. Do not mention internal implementation details such as:
   "tool", "JSON", "task", "API", "planner", or "route".

7. If the evidence is uncertain or verification indicates a problem,
clearly state the uncertainty.

8. Use professional but easy-to-understand language.

Return only the final answer for the user.
"""

        try:
            response = self.llm.generate(prompt)

            if response and response.strip():
                return response.strip()

        except Exception:
            pass

        return self._fallback_response(
            route=route,
            result=analysis_results[0],
        )

    def _fallback_response(
        self,
        route: str,
        result: dict,
    ) -> str:

        if route == "change_analysis":

            change_percentage = result.get(
                "change_percentage",
                0,
            )

            change_detected = result.get(
                "change_detected",
                False,
            )

            vegetation_status = result.get(
                "vegetation_status",
                "unknown",
            )

            mean_ndvi_before = result.get(
                "mean_ndvi_before",
            )

            mean_ndvi_after = result.get(
                "mean_ndvi_after",
            )

            before_date = (
                result.get(
                    "before_sentinel",
                    {},
                ).get("datetime", "unknown")
            )

            after_date = (
                result.get(
                    "after_sentinel",
                    {},
                ).get("datetime", "unknown")
            )

            response = (
                "Change analysis completed.\n\n"
                f"Change detected: {'Yes' if change_detected else 'No'}.\n"
                f"Pixel-level change: {change_percentage}%.\n"
                f"Before observation: {before_date}.\n"
                f"After observation: {after_date}."
            )

            if (
                mean_ndvi_before is not None
                and mean_ndvi_after is not None
            ):
                response += (
                    f"\nMean NDVI before: {mean_ndvi_before}."
                    f"\nMean NDVI after: {mean_ndvi_after}."
                    f"\nVegetation result: "
                    f"{vegetation_status.replace('_', ' ')}."
                )

            return response

        if route == "scene_caption":
            return result.get(
                "caption",
                "Scene analysis completed.",
            )

        return result.get(
            "answer",
            "Image analysis completed.",
        )