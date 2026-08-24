import re
from datetime import datetime

from app.schemas.query import QueryRequest
from app.schemas.task import Task, TaskStatus, TaskType


class TaskPlanner:
    def create_plan(
        self,
        request: QueryRequest,
    ) -> list[Task]:

        query_lower = request.query.lower().strip()

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

        tasks: list[Task] = []

        # =====================================================
        # DETECT REQUIRED ANALYSES
        # =====================================================

        needs_change_analysis = self._needs_change_analysis(
            query_lower
        )

        needs_scene_analysis = self._needs_scene_analysis(
            query_lower
        )

        needs_image_vqa = self._needs_image_vqa(
            request,
            query_lower,
        )

        # =====================================================
        # TASK 1: CHANGE ANALYSIS
        # =====================================================

        if needs_change_analysis:

            change_parameters = parameters.copy()

            dates = self._extract_dates(
                request.query
            )

            if len(dates) >= 2:
                change_parameters["before_date"] = dates[0]
                change_parameters["after_date"] = dates[1]

            # Explicit API dates override extracted dates
            if getattr(
                request,
                "before_date",
                None,
            ):
                change_parameters["before_date"] = (
                    request.before_date
                )

            if getattr(
                request,
                "after_date",
                None,
            ):
                change_parameters["after_date"] = (
                    request.after_date
                )

            tasks.append(
                Task(
                    task_id="task_1",
                    task_type=TaskType.CHANGE_ANALYSIS,
                    description=(
                        "Compare satellite observations and "
                        "detect surface and vegetation changes."
                    ),
                    status=TaskStatus.PENDING,
                    dependencies=[],
                    parameters=change_parameters,
                )
            )

        # =====================================================
        # TASK 2: SCENE / LAND COVER ANALYSIS
        # =====================================================

        if needs_scene_analysis:

            scene_parameters = parameters.copy()

            # If change analysis exists, this task will receive
            # its result through TaskExecutor.
            dependencies = []

            if needs_change_analysis:
                dependencies = ["task_1"]

            tasks.append(
                Task(
                    task_id=f"task_{len(tasks) + 1}",
                    task_type=TaskType.SCENE_CAPTION,
                    description=(
                        "Analyze the overall Earth Observation "
                        "scene, including land cover and visible "
                        "spatial patterns."
                    ),
                    status=TaskStatus.PENDING,
                    dependencies=dependencies,
                    parameters=scene_parameters,
                )
            )

        # =====================================================
        # TASK 3: SINGLE IMAGE VQA
        # =====================================================

        if (
            needs_image_vqa
            and not needs_change_analysis
            and not needs_scene_analysis
        ):

            tasks.append(
                Task(
                    task_id=f"task_{len(tasks) + 1}",
                    task_type=TaskType.SINGLE_IMAGE_VQA,
                    description=(
                        "Answer the user's specific question "
                        "about the provided satellite or aerial "
                        "image."
                    ),
                    status=TaskStatus.PENDING,
                    dependencies=[],
                    parameters=parameters.copy(),
                )
            )

        # =====================================================
        # FALLBACK
        # =====================================================

        if not tasks:

            fallback_type = self._get_task_type(
                request
            )

            tasks.append(
                Task(
                    task_id="task_1",
                    task_type=fallback_type,
                    description=(
                        f"Execute {fallback_type.value} "
                        "for the given remote sensing query."
                    ),
                    status=TaskStatus.PENDING,
                    dependencies=[],
                    parameters=parameters.copy(),
                )
            )

        return tasks

    # =========================================================
    # CHANGE ANALYSIS DETECTION
    # =========================================================

    def _needs_change_analysis(
        self,
        query: str,
    ) -> bool:

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
            "increase",
            "decrease",
            "gain",
            "loss",
        ]

        return any(
            keyword in query
            for keyword in change_keywords
        )

    # =========================================================
    # SCENE ANALYSIS DETECTION
    # =========================================================

    def _needs_scene_analysis(
        self,
        query: str,
    ) -> bool:

        scene_keywords = [
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
            "overall",
            "spatial patterns",
            "landscape",
        ]

        return any(
            keyword in query
            for keyword in scene_keywords
        )

    # =========================================================
    # IMAGE VQA DETECTION
    # =========================================================

    def _needs_image_vqa(
        self,
        request: QueryRequest,
        query: str,
    ) -> bool:

        if not request.image_urls:
            return False

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

        return (
            query.endswith("?")
            or query.startswith(
                tuple(question_starters)
            )
        )

    # =========================================================
    # FALLBACK TASK TYPE
    # =========================================================

    def _get_task_type(
        self,
        request: QueryRequest,
    ) -> TaskType:

        if self._needs_change_analysis(
            request.query.lower()
        ):
            return TaskType.CHANGE_ANALYSIS

        if request.image_urls:
            return TaskType.SINGLE_IMAGE_VQA

        if request.bbox is not None:
            return TaskType.SCENE_CAPTION

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
        # FORMAT: YYYY-MM-DD
        # -----------------------------------------------------

        iso_pattern = (
            r"\b\d{4}-\d{2}-\d{2}\b"
        )

        for match in re.finditer(
            iso_pattern,
            query,
        ):

            try:

                parsed_date = datetime.strptime(
                    match.group(),
                    "%Y-%m-%d",
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

            parsed_date = datetime(
                year,
                month_mapping[month_name],
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