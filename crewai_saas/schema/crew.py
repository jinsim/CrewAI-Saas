from typing import ClassVar
from typing import List, Optional
from datetime import datetime

from crewai_saas.core import CrewStatus
from crewai_saas.schema.base import CreateBase, InDBBase, ResponseBase, UpdateBase


# request
# Properties to receive on item creation
# in
#   public.crew (
#     id bigint generated by default as identity,
#     name character varying not null default ''::character varying,
#     created_at timestamp without time zone not null default now(),
#     description text null,
#     greeting text null,
#     is_sequential boolean not null,
#     input_price numeric null,
#     output_price numeric null,
#     status character varying not null default 'PRIVATE'::character varying,
#     use_history boolean not null default false,
#     usage integer not null default 0,
#     average_token_usage integer not null default 0,
#     updated_at timestamp without time zone not null default now(),
#     is_deleted boolean not null default false,
#     llm_id bigint not null,
#     tags text[] null,
#     constraint crew_pkey primary key (id),
#     constraint crew_id_key unique (id),
#     constraint crew_llm_id_fkey foreign key (llm_id) references llm (id)
class CrewCreate(CreateBase):
    name: str
    description: Optional[str] = ""
    greeting: Optional[str] = ""
    is_sequential: Optional[bool] = False
    input_price: Optional[float] = 0
    output_price: Optional[float] = 0
    status: Optional[CrewStatus] = CrewStatus.PRIVATE
    use_history: Optional[bool] = False
    usage: Optional[int] = 0
    average_token_usage: Optional[int] = 0
    llm_id: Optional[int] = None
    tags: Optional[List[str]] = None
    task_ids: Optional[List[int]] = None


# Properties to receive on item update
# in
class CrewUpdate(UpdateBase):
    name: str
    description: Optional[str] = None
    greeting: Optional[str] = None
    is_sequential: bool
    input_price: Optional[float] = 0
    output_price: Optional[float] = 0
    status: CrewStatus
    use_history: Optional[bool] = False
    updated_at: Optional[str] = str(datetime.now())
    llm_id: Optional[int] = None
    tags: Optional[List[str]] = None
    task_ids: Optional[List[int]] = None


# Properties to return to client
# curd model
# out
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
    tags: Optional[List[str]] = None
    task_ids: Optional[List[int]] = None

    table_name: ClassVar[str] = "crew"

class CrewWithTask(Crew):
    tasks: Optional[tuple] = None


# Properties properties stored in DB
class CrewInDB(InDBBase):
    name: str
    description: Optional[str]
    greeting: Optional[str]
    is_sequential: bool = False
    input_price: Optional[float]
    output_price: Optional[float]
    sstatus: CrewStatus = CrewStatus.PRIVATE
    use_history: bool = False
    usage: int = 0
    average_token_usage: int = 0
    updated_at: str
    is_deleted: bool = False
    llm_id: Optional[int]
    tags: Optional[List[str]]
    task_ids: Optional[List[int]]

#   public.task (
#     id bigint generated by default as identity,
#     crew_id bigint not null,
#     created_at timestamp without time zone not null default now(),
#     name character varying not null,
#     decription text null,
#     expected_output text null,
#     is_deleted boolean not null default false,
#     constraint task_pkey primary key (id),
#     constraint task_id_key unique (id),
#     constraint task_crew_id_fkey foreign key (crew_id) references crew (id)
#   ) tablespace pg_default;
class TaskCreate(CreateBase):
    # 저장할 때는 agent_id 할당 안할 수도 있음. 배포할 때는 되어 있어야 함.
    agent_id: Optional[int] = None
    crew_id: int
    name: str
    description: Optional[str] = ""
    expected_output: Optional[str] = ""

class TaskUpdate(UpdateBase):
    agent_id: Optional[int] = None
    name: str
    description: str
    expected_output: str

class Task(ResponseBase):
    agent_id: Optional[int] = None
    crew_id: int
    name: str
    description: Optional[str]
    expected_output: Optional[str]
    is_deleted: bool

    table_name: ClassVar[str] = "task"

class TaskWithContext(Task):
    context_task_ids: Optional[list] = None

class TaskWithAgent(TaskWithContext):
    agents: Optional[list] = None

class TaskInDB(InDBBase):
    agent_id: Optional[int]
    crew_id: int
    name: str
    description: Optional[str]
    expected_output: Optional[str]
    is_deleted: bool

#   public.task_context (
#     id bigint generated by default as identity,
#     created_at timestamp with time zone not null default now(),
#     parent_task_id bigint null,
#     child_task_id bigint null,
#     constraint task_context_pkey primary key (id),
#     constraint task_context_child_task_id_fkey foreign key (child_task_id) references task (id),
#     constraint task_context_parent_task_id_fkey foreign key (parent_task_id) references task (id)

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

#   public.tool (
#     id bigint generated by default as identity not null,
#     created_at timestamp without time zone not null default now(),
#     name character varying not null,
#     key character varying not null,
#     description text null,
#     is_deleted boolean not null default false,
#     constraint tool_pkey primary key (id),
#     constraint tool_id_key unique (id),
#     constraint tool_key_key unique (key)

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



# public.agent (
#     id bigint generated by default as identity,
#     created_at timestamp without time zone not null default now(),
#     task_id bigint not null,
#     name character varying null,
#     role text null,
#     goal text null,
#     backstory text null,
#     llm_id bigint not null,
#     tools bigint[] null,
#     constraint agent_pkey primary key (id),
#     constraint agent_id_key unique (id),
#     constraint agent_llm_id_fkey foreign key (llm_id) references llm (id),
#     constraint agent_task_id_fkey foreign key (task_id) references task (id)

class AgentCreate(CreateBase):
    crew_id: int
    name: Optional[str] = ""
    role: Optional[str] = ""
    goal: Optional[str] = ""
    backstory: Optional[str] = ""
    llm_id: Optional[int] = None
    tool_ids: Optional[List[int]] = None

class AgentUpdate(UpdateBase):
    name: Optional[str] = ""
    role: Optional[str] = ""
    goal: Optional[str] = ""
    backstory: Optional[str] = ""
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


