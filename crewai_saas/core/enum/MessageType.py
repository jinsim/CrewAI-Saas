from enum import Enum


class MessageType(Enum):
    AGENT = "agent"
    TASK = "task"
    SYSTEM = "system"
    USER = "user"
    FUNCTION_CALL = "function_call"
