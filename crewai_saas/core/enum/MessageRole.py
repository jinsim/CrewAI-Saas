from enum import Enum
class MesssageRole(Enum):
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"
    USER = "USER"
    FUNCTION_CALL = "FUNCTION_CALL"