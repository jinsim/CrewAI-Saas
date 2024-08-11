from typing import ClassVar
from typing import List, Optional
from datetime import datetime

from crewai_saas.core.enum.CrewStatus import CrewStatus

from crewai_saas.model.base import CreateBase, InDBBase, ResponseBase, UpdateBase
from crewai_saas.model.crew import Tool

class PublishedCrewCreate(CreateBase):
    name: str
    description: Optional[str] = None
    greeting: Optional[str] = None
    is_sequential: bool
    input_price: Optional[float] = 0
    output_price: Optional[float] = 0
    status: CrewStatus
    use_history: bool
    usage: int
    average_token_usage: int
    updated_at: str
    is_deleted: bool
    llm_id: int
    tags: Optional[List[str]] = None
    task_ids: Optional[List[int]] = None
    pre_questions: Optional[List[str]] = None
    user_id: int

class PublishedCrewUpdate(UpdateBase):
    name: str
    description: Optional[str] = None
    greeting: Optional[str] = None
    is_sequential: bool
    input_price: Optional[float] = 0
    output_price: Optional[float] = 0
    status: CrewStatus
    use_history: bool
    updated_at: str
    is_deleted: bool
    llm_id: int
    tags: Optional[List[str]] = None
    task_ids: Optional[List[int]] = None
    pre_questions: Optional[List[str]] = None
    user_id: int


class PublishedCrew(ResponseBase):
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
    tags: Optional[List[str]] = None
    task_ids: Optional[List[int]] = None
    pre_questions: Optional[List[str]] = None
    user_id: Optional[int] = None

    table_name: ClassVar[str] = "published_crew"


class PublishedCrewInDB(InDBBase):
    name: str
    description: Optional[str]
    greeting: Optional[str]
    is_sequential: bool = False
    input_price: Optional[float]
    output_price: Optional[float]
    status: CrewStatus
    use_history: bool = False
    usage: int = 0
    average_token_usage: int = 0
    updated_at: str
    is_deleted: bool = False
    llm_id: Optional[int]
    tags: Optional[List[str]]
    task_ids: Optional[List[int]]
    pre_questions: Optional[List[str]]
    user_id: Optional[int] = None


class PublishedTaskCreate(CreateBase):
    agent_id: int
    crew_id: int
    name: str
    description: Optional[str] = None
    expected_output: Optional[str] = None

class PublishedTaskUpdate(UpdateBase):
    agent_id: int
    crew_id: int
    name: str
    description: Optional[str] = None
    expected_output: Optional[str] = None

class PublishedTask(ResponseBase):
    agent_id: int
    crew_id: int
    name: str
    description: Optional[str]
    expected_output: Optional[str]
    is_deleted: bool

    table_name: ClassVar[str] = "published_task"

class PublishedTaskWithContext(PublishedTask):
    context_task_ids: Optional[list] = None

class PublishedTaskInDB(InDBBase):
    agent_id: int
    crew_id: int
    name: str
    description: Optional[str]
    expected_output: Optional[str]
    is_deleted: bool

class PublishedTaskContextCreate(CreateBase):
    parent_task_id: int
    child_task_id: int

class PublishedTaskContextUpdate(UpdateBase):
    parent_task_id: int
    child_task_id: int

class PublishedTaskContext(ResponseBase):
    parent_task_id: int
    child_task_id: int

    table_name: ClassVar[str] = "published_task_context"


class PublishedTaskContextInDB(InDBBase):
    parent_task_id: int
    child_task_id: int

class PublishedAgentCreate(CreateBase):
    crew_id: int
    name: Optional[str] = ""
    role: Optional[str] = ""
    goal: Optional[str] = ""
    backstory: Optional[str] = ""
    llm_id: Optional[int] = None
    tool_ids: Optional[List[int]] = None

class PublishedAgentUpdate(UpdateBase):
    crew_id: int
    name: Optional[str]
    role: Optional[str]
    goal: Optional[str]
    backstory: Optional[str]
    llm_id: Optional[int]
    tool_ids: Optional[List[int]]
    is_deleted: bool

class PublishedAgent(ResponseBase):
    crew_id: int
    name: Optional[str]
    role: Optional[str]
    goal: Optional[str]
    backstory: Optional[str]
    llm_id: Optional[int]
    tool_ids: Optional[List[int]]
    is_deleted: bool

    table_name: ClassVar[str] = "published_agent"


class PublishedAgentWithTool(PublishedAgent):
    tools: Optional[List[Tool]] = None


class PublishedAgentInDB(InDBBase):
    crew_id: int
    name: Optional[str]
    role: Optional[str]
    goal: Optional[str]
    backstory: Optional[str]
    llm_id: Optional[int]
    tools: Optional[list]
    is_deleted: bool


class PublishedCrewWithAll(PublishedCrew):
    tasks: Optional[List[PublishedTaskWithContext]]
    agents: Optional[List[PublishedAgentWithTool]]
