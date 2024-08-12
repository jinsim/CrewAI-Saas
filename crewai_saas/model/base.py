from typing import ClassVar
from typing import Optional


from pydantic import BaseModel, ConfigDict


class CreateBase(BaseModel):
    pass

class UpdateBase(BaseModel):
    pass


class DeleteBase(BaseModel):
    id: int
    is_deleted: Optional[bool] = True

class InDBBase(BaseModel):
    id: int
    created_at: str

class InDBBaseWithoutCreatedAt(BaseModel):
    id: int

class ResponseBase(InDBBase):
    table_name: ClassVar[str] = "ResponseBase".lower()
    Config: ClassVar[ConfigDict] = ConfigDict(
        extra="ignore", arbitrary_types_allowed=True
    )

class ResponseBaseWithoutCreatedAt(InDBBaseWithoutCreatedAt):
    table_name: ClassVar[str] = "ResponseBase".lower()
    Config: ClassVar[ConfigDict] = ConfigDict(
        extra="ignore", arbitrary_types_allowed=True
    )