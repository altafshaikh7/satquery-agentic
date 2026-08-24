from enum import Enum

from pydantic import BaseModel, Field


class TaskType(str, Enum):

    # Core analysis tools
    CHANGE_ANALYSIS = "change_analysis"
    SCENE_CAPTION = "scene_caption"
    SINGLE_IMAGE_VQA = "single_image_vqa"

    # Specialized remote sensing tools
    LAND_COVER_CLASSIFICATION = "land_cover_classification"
    WATER_BODY_DETECTION = "water_body_detection"
    DEFORESTATION_DETECTION = "deforestation_detection"
    URBAN_EXPANSION_ANALYSIS = "urban_expansion_analysis"
    AGRICULTURAL_CROP_ANALYSIS = "agricultural_crop_analysis"

    # Advanced tools
    OBJECT_DETECTION = "object_detection"
    DISASTER_DAMAGE_ASSESSMENT = "disaster_damage_assessment"


class TaskStatus(str, Enum):

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):

    task_id: str
    task_type: TaskType
    description: str

    status: TaskStatus = TaskStatus.PENDING

    dependencies: list[str] = Field(
        default_factory=list
    )

    parameters: dict = Field(
        default_factory=dict
    )