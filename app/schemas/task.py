from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    task_id: str
    name: str
    tool_name: str
    status: TaskStatus = TaskStatus.PENDING
    input_data: dict = Field(default_factory=dict)
    output_data: dict | None = None
    error: str | None = None