from app.agent.executor import TaskExecutor
from app.agent.planner import TaskPlanner
from app.agent.router import QueryRouter
from app.agent.synthesizer import ResponseSynthesizer
from app.agent.verifier import ResultVerifier
from app.schemas.query import QueryRequest
from app.tools.confidence_estimator import ConfidenceEstimator
from app.tools.evidence_extractor import EvidenceExtractor


class AgentGraph:
    def __init__(self):
        self.router = QueryRouter()
        self.planner = TaskPlanner()
        self.executor = TaskExecutor()
        self.verifier = ResultVerifier()
        self.evidence_extractor = EvidenceExtractor()
        self.confidence_estimator = ConfidenceEstimator()
        self.synthesizer = ResponseSynthesizer()

    def run(
        self,
        request: QueryRequest,
    ) -> dict:

        # --------------------------------------------------
        # 1. ROUTE QUERY
        # --------------------------------------------------

        route = self.router.route(request)

        # --------------------------------------------------
        # 2. CREATE TASK PLAN
        # --------------------------------------------------

        tasks = self.planner.create_plan(request)

        # --------------------------------------------------
        # 3. EXECUTE TASKS
        # --------------------------------------------------

        results = self.executor.execute_all(tasks)

        # --------------------------------------------------
        # 4. VERIFY EXECUTION RESULTS
        # --------------------------------------------------

        verification = self.verifier.verify(results)

        # --------------------------------------------------
        # 5. EXTRACT EVIDENCE + ESTIMATE CONFIDENCE
        # --------------------------------------------------

        all_evidence = []
        tool_confidences = []

        for execution_result in results:

            if execution_result.get("status") != "completed":
                continue

            tool_result = execution_result.get(
                "result",
                {},
            )

            # Extract evidence from successful tool result
            evidence = self.evidence_extractor.extract(
                tool_result
            )

            all_evidence.extend(evidence)

            # Estimate confidence for this tool result
            confidence = self.confidence_estimator.estimate(
                tool_result
            )

            tool_confidences.append(confidence)

            # Attach evidence and confidence to task result
            execution_result["evidence"] = evidence
            execution_result["confidence"] = confidence

        # --------------------------------------------------
        # 6. CALCULATE FINAL CONFIDENCE
        # --------------------------------------------------

        if tool_confidences:
            analysis_confidence = round(
                sum(tool_confidences)
                / len(tool_confidences),
                2,
            )
        else:
            analysis_confidence = 0.0

        # Combine execution verification with analysis confidence
        final_confidence = round(
            (
                verification["confidence"]
                + analysis_confidence
            )
            / 2,
            2,
        )

        # --------------------------------------------------
        # 7. GENERATE FINAL ANSWER
        # --------------------------------------------------

        answer = self.synthesizer.synthesize(
            query=request.query,
            route=route,
            results=results,
            verification=verification,
        )

        # --------------------------------------------------
        # 8. RETURN COMPLETE RESPONSE
        # --------------------------------------------------

        return {
            "query": request.query,
            "route": route,
            "tasks": [
                task.model_dump(mode="json")
                for task in tasks
            ],
            "results": results,
            "evidence": all_evidence,
            "verification": verification,
            "answer": answer,
            "confidence": final_confidence,
        }