from typing import ClassVar
from typing import List, Optional
from datetime import datetime

from crewai_saas.core.enum.CrewStatus import CrewStatus

from crewai_saas.model.base import CreateBase, InDBBase, ResponseBase, UpdateBase
class CrewCreate(CreateBase):
    user_id: int

class CrewUpdate(UpdateBase):
    name: Optional[str] = None
    description: Optional[str] = None
    greeting: Optional[str] = None
    is_sequential: Optional[bool] = None
    input_price: Optional[float] = None
    output_price: Optional[float] = None
    status: Optional[CrewStatus] = None  # Assuming it's a string for simplicity
    use_history: Optional[bool] = None
    updated_at: Optional[str] = str(datetime.now())
    llm_id: Optional[int] = None
    tags: Optional[List[str]] = None
    task_ids: Optional[List[int]] = None
    pre_questions: Optional[List[str]] = None

    class Config:
        use_enum_values = True

class Crew(ResponseBase):
    name: str
    description: Optional[str]
    greeting: Optional[str]
    is_sequential: bool
    input_price: Optional[float]
    output_price: Optional[float]
    status: CrewStatus
    use_history: bool
    usage: int
    average_token_usage: int
    updated_at: str
    is_deleted: bool
    llm_id: Optional[int]
    tags: Optional[List[str]]
    task_ids: Optional[List[int]]
    pre_questions: Optional[List[str]]
    user_id: Optional[int]

    table_name: ClassVar[str] = "crew"
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True


class CrewInDB(InDBBase):
    name: str
    description: Optional[str]
    greeting: Optional[str]
    is_sequential: bool
    input_price: Optional[float]
    output_price: Optional[float]
    status: CrewStatus
    use_history: bool
    usage: int
    average_token_usage: int
    updated_at: str
    is_deleted: bool
    llm_id: Optional[int]
    tags: Optional[List[str]]
    task_ids: Optional[List[int]]
    pre_questions: Optional[List[str]]
    user_id: Optional[int]
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

class TaskCreate(CreateBase):
    agent_id: Optional[int] = None
    crew_id: int
    name: str
    description: Optional[str] = ""
    expected_output: Optional[str] = ""
    context_task_ids: Optional[list] = None

class TaskUpdate(UpdateBase):
    agent_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    expected_output: Optional[str] = None
    context_task_ids: Optional[list] = None

class Task(ResponseBase):
    agent_id: Optional[int] = None
    crew_id: int
    name: str
    description: Optional[str]
    expected_output: Optional[str]
    is_deleted: bool
    context_task_ids: Optional[list]

    table_name: ClassVar[str] = "task"

class TaskWithContext(Task):
    context_task_ids: Optional[list] = None

class TaskInDB(InDBBase):
    agent_id: Optional[int]
    crew_id: int
    name: str
    description: Optional[str]
    expected_output: Optional[str]
    is_deleted: bool
    context_task_ids: Optional[list]

class TaskContextCreate(CreateBase):
    parent_task_id: int
    child_task_id: int

class TaskContextUpdate(UpdateBase):
    parent_task_id: int
    child_task_id: int

class TaskContext(ResponseBase):
    parent_task_id: int
    child_task_id: int

    table_name: ClassVar[str] = "task_context"


class TaskContextInDB(InDBBase):
    parent_task_id: int
    child_task_id: int

class ToolCreate(CreateBase):
    name: str
    key: str
    description: Optional[str] = ""
    is_deleted: Optional[bool] = False

class ToolUpdate(UpdateBase):
    name: str
    key: str
    description: Optional[str] = ""
    is_deleted: Optional[bool] = False

class Tool(ResponseBase):
    name: str
    key: str
    description: Optional[str]
    is_deleted: bool

    table_name: ClassVar[str] = "tool"

class ToolInDB(InDBBase):
    name: str
    key: str
    description: Optional[str]
    is_deleted: bool

class AgentCreate(CreateBase):
    crew_id: int
    name: Optional[str] = ""
    role: Optional[str] = ""
    goal: Optional[str] = ""
    backstory: Optional[str] = ""
    llm_id: Optional[int] = None
    tool_ids: Optional[List[int]] = None

class AgentUpdate(UpdateBase):
    name: Optional[str] = None
    role: Optional[str] = None
    goal: Optional[str] = None
    backstory: Optional[str] = None
    llm_id: Optional[int] = None
    tool_ids: Optional[List[int]] = None

class Agent(ResponseBase):
    crew_id: int
    name: Optional[str]
    role: Optional[str]
    goal: Optional[str]
    backstory: Optional[str]
    llm_id: Optional[int]
    tool_ids: Optional[List[int]]
    is_deleted: bool

    table_name: ClassVar[str] = "agent"


class AgentWithTool(Agent):
    tools: Optional[List[Tool]] = None


class AgentInDB(InDBBase):
    crew_id: int
    name: Optional[str]
    role: Optional[str]
    goal: Optional[str]
    backstory: Optional[str]
    llm_id: Optional[int]
    tools: Optional[list]
    is_deleted: bool


class CrewWithAll(Crew):
    tasks: Optional[List[Task]]
    agents: Optional[List[AgentWithTool]]
