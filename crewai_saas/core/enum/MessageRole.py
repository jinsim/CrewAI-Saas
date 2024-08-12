from enum import Enum


class MessageRole(Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"
    FUNCTION_CALL = "function_call"
