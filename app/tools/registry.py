from app.tools.change_analysis import ChangeAnalysisTool
from app.tools.scene_caption import SceneCaptionTool
from app.tools.single_image_vqa import SingleImageVQATool


class ToolRegistry:
    def __init__(self):
        self._tools = {
            "change_analysis": ChangeAnalysisTool(),
            "scene_caption": SceneCaptionTool(),
            "single_image_vqa": SingleImageVQATool(),
        }

    def get_tool(self, name: str):
        tool = self._tools.get(name)

        if tool is None:
            raise ValueError(f"Tool not found: {name}")

        return tool

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())