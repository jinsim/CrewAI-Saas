from typing import ClassVar
from typing import Optional


from crewai_saas.model.base import CreateBase, InDBBase, ResponseBase, UpdateBase, ResponseBaseWithoutCreatedAt, InDBBaseWithoutCreatedAt


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
    is_new_user: Optional[bool] = False
    table_name: ClassVar[str] = "user"

class UserInDB(InDBBase):
    name: Optional[str] = ""
    email: Optional[str] = ""
    image: Optional[str] = ""
    coin: Optional[float] = 0
    is_deleted: Optional[bool] = False
    country_id: Optional[int] = None


class Country(ResponseBaseWithoutCreatedAt):
    name: Optional[str] = ""
    continent_name: Optional[str] = ""
    code: Optional[str] = ""

    table_name: ClassVar[str] = "country"

class CountryInDB(InDBBaseWithoutCreatedAt):
    name: Optional[str] = ""
    continent_name: Optional[str] = ""
    code: Optional[str] = ""

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

