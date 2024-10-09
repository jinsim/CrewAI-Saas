from typing import ClassVar
from typing import List, Optional

from crewai_saas.core.enum.CrewStatus import CrewStatus

from crewai_saas.model.base import CreateBase, InDBBase, ResponseBase, UpdateBase
from crewai_saas.model.crew import Tool

class PublishedCrewCreate(CreateBase):
    crew_id: int
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
    llm_id: Optional[int]
    tags: Optional[List[str]] = None
    pre_questions: Optional[List[str]] = None
    profile_id: Optional[int]
    image: Optional[str] = None
    detail: Optional[str] = None
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

class PublishedCrew(ResponseBase):
    crew_id: int
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
    published_task_ids: Optional[List[int]]
    pre_questions: Optional[List[str]]
    profile_id: Optional[int]
    image: Optional[str]
    detail: Optional[str]

    table_name: ClassVar[str] = "published_crew"
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True


class PublishedCrewInDB(InDBBase):
    crew_id: int
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
    published_task_ids: Optional[List[int]]
    pre_questions: Optional[List[str]]
    profile_id: Optional[int] = None
    image: Optional[str]
    detail: Optional[str]
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True


class PublishedTaskCreate(CreateBase):
    published_agent_id: int
    published_crew_id: int
    name: str
    description: Optional[str] = None
    expected_output: Optional[str] = None
    is_deleted: bool
    context_published_task_ids: Optional[list] = None


class PublishedTask(ResponseBase):
    published_agent_id: int
    published_crew_id: int
    name: str
    description: Optional[str]
    expected_output: Optional[str]
    is_deleted: bool
    context_published_task_ids: Optional[list]

    table_name: ClassVar[str] = "published_task"

class PublishedTaskWithContext(PublishedTask):
    context_published_task_ids: Optional[list] = None

class PublishedTaskInDB(InDBBase):
    published_agent_id: int
    published_crew_id: int
    name: str
    description: Optional[str]
    expected_output: Optional[str]
    is_deleted: bool
    context_published_task_ids: Optional[list]

class PublishedAgentCreate(CreateBase):
    published_crew_id: int
    name: Optional[str] = ""
    role: Optional[str] = ""
    goal: Optional[str] = ""
    backstory: Optional[str] = ""
    llm_id: Optional[int] = None
    tool_ids: Optional[List[int]] = None
    is_deleted: bool

class PublishedAgent(ResponseBase):
    published_crew_id: int
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
    published_crew_id: int
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
