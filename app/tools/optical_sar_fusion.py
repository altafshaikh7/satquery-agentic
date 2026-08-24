from typing import Any


class OpticalSARFusionTool:

    def fuse(
        self,
        optical_result: dict[str, Any],
        sar_result: dict[str, Any],
    ) -> dict[str, Any]:

        if optical_result.get("status") != "success":
            return {
                "status": "failed",
                "error": "Optical analysis was not successful.",
            }

        if sar_result.get("status") != "success":
            return {
                "status": "failed",
                "error": "SAR analysis was not successful.",
            }

        return {
            "status": "success",
            "tool": "optical_sar_fusion",
            "optical": optical_result,
            "sar": sar_result,
            "fusion": {
                "status": "prepared",
                "description": (
                    "Optical and SAR results were successfully "
                    "combined for joint interpretation."
                ),
            },
        }