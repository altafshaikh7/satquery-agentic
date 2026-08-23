from typing import Any

from app.schemas.task import TaskType
from app.tools.base import BaseTool
from app.tools.change_analysis import ChangeAnalysisTool
from app.tools.scene_caption import SceneCaptionTool
from app.tools.single_image_vqa import SingleImageVQATool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[TaskType, BaseTool] = {
            TaskType.CHANGE_ANALYSIS: ChangeAnalysisTool(),
            TaskType.SCENE_CAPTION: SceneCaptionTool(),
            TaskType.SINGLE_IMAGE_VQA: SingleImageVQATool(),
        }

    def get_tool(self, task_type: TaskType) -> BaseTool:
        tool = self._tools.get(task_type)

        if tool is None:
            raise ValueError(
                f"No tool registered for task type: {task_type.value}"
            )

        return tool

    def list_tools(self) -> list[str]:
        return [task_type.value for task_type in self._tools]

    def execute(
        self,
        task_type: TaskType,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        tool = self.get_tool(task_type)
        return tool.run(parameters)