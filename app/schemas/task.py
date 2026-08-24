from enum import Enum

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    CHANGE_ANALYSIS = "change_analysis"
    SCENE_CAPTION = "scene_caption"
    SINGLE_IMAGE_VQA = "single_image_vqa"


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    task_id: str
    task_type: TaskType
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = Field(default_factory=list)
    parameters: dict = Field(default_factory=dict)