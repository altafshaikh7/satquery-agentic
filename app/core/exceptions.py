class SatQueryError(Exception):
    pass


class ToolExecutionError(SatQueryError):
    pass


class InvalidQueryError(SatQueryError):
    pass