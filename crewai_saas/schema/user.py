from typing import ClassVar
from typing import Optional
from datetime import datetime

from crewai_saas.schema.base import CreateBase, InDBBase, ResponseBase, UpdateBase, ResponseBaseWithoutCreatedAt, InDBBaseWithoutCreatedAt

#   public.user (
#     id bigint generated by default as identity not null,
#     created_at timestamp without time zone not null default now(),
#     name character varying null,
#     email text null,
#     image text null,
#     coin numeric null,
#     updated_at timestamp without time zone not null default now(),
#     is_deleted boolean not null default false,
#     country_id bigint null,
#     constraint user_pkey primary key (id),
#     constraint user_country_id_fkey foreign key (country_id) references country (id)

class UserCreate(CreateBase):
    name: Optional[str] = ""
    email: Optional[str] = ""
    image: Optional[str] = ""
    coin: Optional[float] = 0
    is_deleted: Optional[bool] = False
    country_id: Optional[int] = None

class UserUpdate(UpdateBase):
    name: str
    email: str
    image: Optional[str] = ""
    coin: Optional[float] = 0
    country_id: Optional[int] = None

class User(ResponseBase):
    name: Optional[str] = ""
    email: Optional[str] = ""
    image: Optional[str] = ""
    coin: Optional[float] = 0
    is_deleted: Optional[bool] = False
    country_id: Optional[int] = None

    table_name: ClassVar[str] = "user"

class UserInDB(InDBBase):
    name: Optional[str] = ""
    email: Optional[str] = ""
    image: Optional[str] = ""
    coin: Optional[float] = 0
    is_deleted: Optional[bool] = False
    country_id: Optional[int] = None


# public.country (
#     id bigint generated by default as identity not null,
#     name character varying null,
#     continent_name character varying null,
#     code character varying null,
#     constraint contry_pkey primary key (id),
#     constraint country_id_key unique (id)


class Country(ResponseBaseWithoutCreatedAt):
    name: Optional[str] = ""
    continent_name: Optional[str] = ""
    code: Optional[str] = ""

    table_name: ClassVar[str] = "country"

class CountryInDB(InDBBaseWithoutCreatedAt):
    name: Optional[str] = ""
    continent_name: Optional[str] = ""
    code: Optional[str] = ""

#   public.api_key (
#     id bigint generated by default as identity not null,
#     created_at timestamp without time zone not null default now(),
#     updated_at timestamp without time zone not null default now(),
#     name character varying null,
#     value character varying null,
#     user_id bigint null,
#     llm_provider_id bigint not null,
#     constraint api_key_pkey primary key (id),
#     constraint api_key_id_key unique (id),
#     constraint api_key_llm_provider_id_fkey foreign key (llm_provider_id) references llm_provider (id),
#     constraint api_key_user_id_fkey foreign key (user_id) references "user" (id)

class ApiKeyCreate(CreateBase):
    name: Optional[str] = ""
    value: Optional[str] = ""
    user_id: Optional[int] = None
    llm_provider_id: int

class ApiKeyUpdate(UpdateBase):
    name: Optional[str] = ""
    value: Optional[str] = ""
    user_id: Optional[int] = None
    llm_provider_id: int

class ApiKey(ResponseBase):
    name: Optional[str] = ""
    value: Optional[str] = ""
    user_id: Optional[int] = None
    llm_provider_id: int

    table_name: ClassVar[str] = "api_key"

class ApiKeyInDB(InDBBase):
    name: Optional[str] = ""
    value: Optional[str] = ""
    user_id: Optional[int] = None
    llm_provider_id: int
