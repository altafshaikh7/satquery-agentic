import re
from datetime import datetime

from app.schemas.query import QueryRequest
from app.schemas.task import Task, TaskStatus, TaskType


class TaskPlanner:
    def create_plan(
        self,
        request: QueryRequest,
    ) -> list[Task]:

        # =====================================================
        # DETECT TASK TYPE
        # =====================================================

        task_type = self._get_task_type(
            request
        )

        # =====================================================
        # BASE PARAMETERS
        # =====================================================

        parameters = {
            "query": request.query,
            "question": request.query,
            "image_urls": request.image_urls,
        }

        if request.bbox is not None:
            parameters["bbox"] = request.bbox

        # =====================================================
        # CHANGE ANALYSIS DATE EXTRACTION
        # =====================================================

        if task_type == TaskType.CHANGE_ANALYSIS:

            dates = self._extract_dates(
                request.query
            )

            # Extract dates from query
            if len(dates) >= 2:
                parameters["before_date"] = dates[0]
                parameters["after_date"] = dates[1]

            # Explicit API dates override extracted dates
            if getattr(
                request,
                "before_date",
                None,
            ):
                parameters["before_date"] = (
                    request.before_date
                )

            if getattr(
                request,
                "after_date",
                None,
            ):
                parameters["after_date"] = (
                    request.after_date
                )

        # =====================================================
        # CREATE TASK
        # =====================================================

        task = Task(
            task_id="task_1",
            task_type=task_type,
            description=(
                f"Execute {task_type.value} "
                "for the given remote sensing query"
            ),
            status=TaskStatus.PENDING,
            dependencies=[],
            parameters=parameters,
        )

        return [task]

    # =========================================================
    # DETECT TASK TYPE
    # =========================================================

    def _get_task_type(
        self,
        request: QueryRequest,
    ) -> TaskType:

        query_lower = request.query.lower().strip()

        # =====================================================
        # 1. CHANGE ANALYSIS
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
            keyword in query_lower
            for keyword in change_keywords
        ):
            return TaskType.CHANGE_ANALYSIS

        # =====================================================
        # 2. SINGLE IMAGE VQA
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
            query_lower.endswith("?")
            or query_lower.startswith(
                tuple(question_starters)
            )
        ):
            return TaskType.SINGLE_IMAGE_VQA

        # =====================================================
        # 3. SCENE CAPTION
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
            "water body",
            "water bodies",
            "infrastructure",
            "forest",
            "agriculture",
            "agricultural",
            "urban",
            "built-up",
            "roads",
            "road",
            "river",
            "lake",
            "reservoir",
            "satellite image",
            "remote sensing",
            "what is visible",
            "what can you see",
        ]

        if any(
            keyword in query_lower
            for keyword in scene_keywords
        ):
            return TaskType.SCENE_CAPTION

        # =====================================================
        # 4. BBOX DEFAULT
        # =====================================================

        if request.bbox is not None:
            return TaskType.SCENE_CAPTION

        # =====================================================
        # 5. DEFAULT
        # =====================================================

        return TaskType.SINGLE_IMAGE_VQA

    # =========================================================
    # EXTRACT DATES FROM QUERY
    # =========================================================

    def _extract_dates(
        self,
        query: str,
    ) -> list[str]:

        extracted_dates: list[
            tuple[int, str]
        ] = []

        # -----------------------------------------------------
        # FORMAT: 2025-01-15
        # -----------------------------------------------------

        iso_pattern = (
            r"\b\d{4}-\d{2}-\d{2}\b"
        )

        for match in re.finditer(
            iso_pattern,
            query,
        ):

            date_text = match.group()

            try:

                parsed_date = (
                    datetime.strptime(
                        date_text,
                        "%Y-%m-%d",
                    )
                )

                extracted_dates.append(
                    (
                        match.start(),
                        parsed_date.strftime(
                            "%Y-%m-%d"
                        ),
                    )
                )

            except ValueError:
                pass

        # -----------------------------------------------------
        # FORMAT:
        # January 2025
        # Jan 2025
        # -----------------------------------------------------

        month_pattern = (
            r"\b("
            r"january|february|march|april|may|"
            r"june|july|august|september|"
            r"october|november|december|"
            r"jan|feb|mar|apr|jun|jul|aug|"
            r"sep|sept|oct|nov|dec"
            r")\s+(\d{4})\b"
        )

        month_mapping = {
            "january": 1,
            "jan": 1,
            "february": 2,
            "feb": 2,
            "march": 3,
            "mar": 3,
            "april": 4,
            "apr": 4,
            "may": 5,
            "june": 6,
            "jun": 6,
            "july": 7,
            "jul": 7,
            "august": 8,
            "aug": 8,
            "september": 9,
            "sep": 9,
            "sept": 9,
            "october": 10,
            "oct": 10,
            "november": 11,
            "nov": 11,
            "december": 12,
            "dec": 12,
        }

        for match in re.finditer(
            month_pattern,
            query,
            re.IGNORECASE,
        ):

            month_name = (
                match.group(1).lower()
            )

            year = int(
                match.group(2)
            )

            month = month_mapping[
                month_name
            ]

            parsed_date = datetime(
                year,
                month,
                1,
            )

            extracted_dates.append(
                (
                    match.start(),
                    parsed_date.strftime(
                        "%Y-%m-%d"
                    ),
                )
            )

        # -----------------------------------------------------
        # SORT BY QUERY POSITION
        # -----------------------------------------------------

        extracted_dates.sort(
            key=lambda item: item[0]
        )

        return [
            date_value
            for _, date_value
            in extracted_dates
        ]