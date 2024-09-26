from typing import ClassVar
from typing import Optional
from crewai_saas.core.enum import CycleStatus, MessageRole, MessageType
from pydantic import BaseModel

from crewai_saas.model.base import CreateBase, InDBBase, ResponseBase, UpdateBase
from crewai_saas.model.published_crew import PublishedCrew


class EmployedCrewCreate(CreateBase):
    crew_id: int
    profile_id: int

class EmployedCrewUpdate(UpdateBase):
    is_favorite: bool

class EmployedCrew(ResponseBase):
    crew_id: int
    profile_id: int
    is_favorite: bool
    is_deleted: bool
    is_owner: bool

    table_name: ClassVar[str] = "employed_crew"

class EmployedCrewInDB(InDBBase):
    crew_id: int
    profile_id: int
    is_favorite: bool
    is_deleted: bool
    is_owner: bool

class EmployedCrewWithCrew(EmployedCrew):
    published_crew: PublishedCrew

class ChatCreate(CreateBase):
    employed_crew_id: int

class ChatUpdate(UpdateBase):
    title: str

class Chat(ResponseBase):
    employed_crew_id: int
    is_deleted: bool
    title: str

    table_name: ClassVar[str] = "chat"

class ChatInDB(InDBBase):
    employed_crew_id: int
    is_deleted: bool
    title: str

class MessageRequest(BaseModel):
    content: str
    role: MessageRole

class MessageCreate(CreateBase):
    content: str
    task_id: Optional[int] = None
    cycle_id: int
    role: MessageRole
    chat_id: int
    agent_id: Optional[int] = None
    type: Optional[MessageType] = None
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

class MessageUpdate(UpdateBase):
    cost: Optional[float] = 0
    input_token: Optional[int] = None
    output_token: Optional[int] = None
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True


class Message(ResponseBase):
    cost: Optional[float]
    input_token: Optional[int]
    output_token: Optional[int]
    content: str
    task_id: Optional[int]
    cycle_id: int
    role: MessageRole
    chat_id: int
    agent_id: Optional[int]
    type: Optional[MessageType]

    table_name: ClassVar[str] = "message"

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

class MessageInDB(InDBBase):
    cost: float
    input_token: int
    output_token: int
    content: str
    task_id: int
    cycle_id: int
    role: MessageRole
    chat_id: int
    agent_id: int
    type: MessageType
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

class MessageSimple(InDBBase):
    content: str
    role: MessageRole
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True



class CycleCreate(CreateBase):
    chat_id: int
    execution_id: Optional[str] = None
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True



class CycleUpdate(UpdateBase):
    status: CycleStatus
    cost: Optional[float] = None
    price: Optional[float] = None
    total_token: Optional[int] = None
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

class CycleUpdateStatus(UpdateBase):
    status: CycleStatus
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

class Cycle(ResponseBase):
    status: CycleStatus
    execution_id: Optional[str]
    cost: Optional[float]
    price: Optional[float]
    total_token: Optional[int]
    chat_id: Optional[int]

    table_name: ClassVar[str] = "cycle"
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

class CycleInDB(InDBBase):
    status: CycleStatus
    execution_id: Optional[str]
    cost: Optional[float]
    price: Optional[float]
    total_token: Optional[int]
    chat_id: Optional[int]
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

class CycleWithMessage(Cycle):
    messages: list[MessageSimple]

class ChatWithCycle(Chat):
    cycle: CycleWithMessage

class ChatWithCycleList(Chat):
    is_owner: bool
    cycles: list[CycleWithMessage]