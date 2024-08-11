from enum import Enum


class MessageRole(Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"
    FUNCTION_CALL = "function_call" # Task 내부에서 CrewAI 가 돌릴 때 발생 (Tool 사용). 쓸 일이 아직 없다.
