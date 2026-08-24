from app.schemas.query import QueryRequest
from app.schemas.task import TaskType


class QueryRouter:
    def route(
        self,
        request: QueryRequest,
    ) -> str:

        query = request.query.lower().strip()

        # =====================================================
        # 1. CHANGE ANALYSIS - HIGHEST PRIORITY
        # =====================================================

        change_keywords = [
            "change",
            "compare",
            "comparison",
            "difference",
            "different",
            "changed",
            "change detection",
            "before",
            "after",
            "between",
            "compared",
        ]

        if any(
            keyword in query
            for keyword in change_keywords
        ):
            return TaskType.CHANGE_ANALYSIS.value

        # =====================================================
        # 2. SINGLE IMAGE VQA
        # Specific questions about an image
        # =====================================================

        question_starters = [
            "is ",
            "are ",
            "what ",
            "where ",
            "which ",
            "how ",
            "can ",
            "does ",
            "do ",
            "did ",
            "was ",
            "were ",
        ]

        if (
            query.endswith("?")
            or query.startswith(
                tuple(question_starters)
            )
        ):
            return TaskType.SINGLE_IMAGE_VQA.value

        # =====================================================
        # 3. SCENE CAPTION
        # General scene analysis / description
        # =====================================================

        scene_keywords = [
            "caption",
            "describe",
            "description",
            "scene",
            "analyze",
            "analyse",
            "analysis",
            "land use",
            "land cover",
            "vegetation",
            "forest",
            "agriculture",
            "agricultural",
            "urban",
            "built-up",
            "infrastructure",
            "road",
            "roads",
            "river",
            "lake",
            "reservoir",
            "satellite image",
            "remote sensing",
            "what is visible",
            "what can you see",
        ]

        if any(
            keyword in query
            for keyword in scene_keywords
        ):
            return TaskType.SCENE_CAPTION.value

        # =====================================================
        # 4. BBOX DEFAULT
        # =====================================================

        if request.bbox is not None:
            return TaskType.SCENE_CAPTION.value

        # =====================================================
        # 5. DEFAULT
        # =====================================================

        return TaskType.SINGLE_IMAGE_VQA.value