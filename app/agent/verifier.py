from app.tools.confidence_estimator import ConfidenceEstimator
from app.tools.evidence_extractor import EvidenceExtractor
from app.tools.geospatial_validator import GeospatialValidator


class ResultVerifier:

    def __init__(self):
        self.evidence_extractor = EvidenceExtractor()
        self.confidence_estimator = ConfidenceEstimator()
        self.geospatial_validator = GeospatialValidator()

    def verify(
        self,
        results: list[dict],
    ) -> dict:

        successful_results = [
            result
            for result in results
            if result.get("status") == "completed"
        ]

        all_evidence = []
        confidence_scores = []
        validation_errors = []

        for execution_result in successful_results:

            tool_result = execution_result.get(
                "result",
                {},
            )

            # --------------------------------------------
            # EXTRACT EVIDENCE
            # --------------------------------------------

            evidence = self.evidence_extractor.extract(
                tool_result
            )

            all_evidence.extend(evidence)

            # --------------------------------------------
            # ESTIMATE TOOL CONFIDENCE
            # --------------------------------------------

            tool_confidence = (
                self.confidence_estimator.estimate(
                    tool_result
                )
            )

            confidence_scores.append(
                tool_confidence
            )

            # --------------------------------------------
            # VALIDATE BBOX IF AVAILABLE
            # --------------------------------------------

            parameters = execution_result.get(
                "parameters",
                {},
            )

            bbox = parameters.get("bbox")

            if bbox is not None:
                is_valid = (
                    self.geospatial_validator.validate_bbox(
                        bbox
                    )
                )

                if not is_valid:
                    validation_errors.append(
                        {
                            "task_id": execution_result.get(
                                "task_id"
                            ),
                            "error": "Invalid geographic bounding box.",
                        }
                    )

        # --------------------------------------------
        # CALCULATE FINAL CONFIDENCE
        # --------------------------------------------

        if not results:
            confidence = 0.0

        elif confidence_scores:

            average_tool_confidence = (
                sum(confidence_scores)
                / len(confidence_scores)
            )

            completion_ratio = (
                len(successful_results)
                / len(results)
            )

            confidence = round(
                average_tool_confidence
                * completion_ratio,
                2,
            )

        else:
            confidence = 0.0

        # --------------------------------------------
        # FINAL VERIFICATION
        # --------------------------------------------

        verified = (
            len(successful_results) > 0
            and not validation_errors
        )

        return {
            "verified": verified,
            "confidence": confidence,
            "successful_tasks": len(
                successful_results
            ),
            "total_tasks": len(results),
            "evidence": all_evidence,
            "validation_errors": validation_errors,
        }