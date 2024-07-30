from typing import ClassVar
from typing import Optional
from datetime import datetime

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
    is_sequential: bool = False
    input_price: Optional[float] = 0
    output_price: Optional[float] = 0
    status: str = "PRIVATE"
    use_history: Optional[bool] = False
    usage: Optional[int] = 0
    average_token_usage: Optional[int] = 0
    is_deleted: bool = False
    llm_id: Optional[int] = None
    tags: Optional[list] = None





# Properties to receive on item update
# in
class CrewUpdate(UpdateBase):
    name: str
    description: Optional[str] = None
    greeting: Optional[str] = None
    is_sequential: bool
    input_price: Optional[float] = 0
    output_price: Optional[float] = 0
    status: str
    use_history: Optional[bool] = False
    updated_at: Optional[str] = str(datetime.now())
    llm_id: Optional[int] = None
    tags: Optional[list] = None


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
    status: str
    use_history: bool
    usage: int
    average_token_usage: int
    updated_at: str
    is_deleted: bool
    llm_id: int
    tags: Optional[list]



    table_name: ClassVar[str] = "crew"


# Properties properties stored in DB
class CrewInDB(InDBBase):
    name: str
    description: Optional[str]
    greeting: Optional[str]
    is_sequential: bool = False
    input_price: Optional[float]
    output_price: Optional[float]
    status: str = "PRIVATE"
    use_history: bool = False
    usage: int = 0
    average_token_usage: int = 0
    updated_at: str
    is_deleted: bool = False
    llm_id: int
    tags: Optional[list]
