from enum import Enum


class CycleStatus(Enum):
    STARTED = "STARTED"
    ERROR = "ERROR"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"
