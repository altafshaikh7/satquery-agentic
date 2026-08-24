class RecoveryManager:
    def recover(self, error: Exception) -> dict:
        return {
            "recovered": False,
            "message": str(error),
        }