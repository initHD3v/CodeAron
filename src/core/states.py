from enum import Enum
from typing import Optional

class AronState(Enum):
    IDLE = "IDLE"
    ANALYZING = "ANALYZING"
    PLANNING = "PLANNING"
    ROUTING = "ROUTING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    CRITIQUING = "CRITIQUING"
    REFINING = "REFINING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"

class ExecutionResult:
    def __init__(self, success: bool, output: str, error: Optional[str] = None, exit_code: int = 0):
        self.success = success
        self.output = output
        self.error = error
        self.exit_code = exit_code
