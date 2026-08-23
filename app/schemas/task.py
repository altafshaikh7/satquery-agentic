from enum import Enum

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    SINGLE_IMAGE_VQA = "single_image_vqa"
    CHANGE_ANALYSIS = "change_analysis"
    SCENE_CAPTION = "scene_caption"
    TEXT_GROUNDING = "text_grounding"
    OPTICAL_SAR_FUSION = "optical_sar_fusion"
    METADATA_VALIDATION = "metadata_validation"
    GEOSPATIAL_VALIDATION = "geospatial_validation"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    task_id: str
    task_type: TaskType
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = Field(default_factory=list)
    parameters: dict = Field(default_factory=dict)