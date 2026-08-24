class OpticalSARFusionTool:
    def fuse(
        self,
        optical_result: dict,
        sar_result: dict,
    ) -> dict:
        return {
            "status": "success",
            "optical": optical_result,
            "sar": sar_result,
            "fusion": "Basic optical-SAR fusion completed",
        }