from enum import Enum


class MessageRole(Enum):
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"
    USER = "USER"
    FUNCTION_CALL = "FUNCTION_CALL"
