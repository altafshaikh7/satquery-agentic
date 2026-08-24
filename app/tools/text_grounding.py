class EvidenceExtractor:
    def extract(self, result: dict) -> list[dict]:
        evidence = []

        if result.get("status") == "success":
            evidence.append(
                {
                    "source": result.get("tool"),
                    "description": "Tool execution completed successfully",
                    "confidence": 0.85,
                }
            )

        return evidence