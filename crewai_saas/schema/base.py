from typing import ClassVar
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict

# request


# Shared properties
# class CRUDBaseModel(BaseModel):
#     # where the data
#     table_name: str


# Properties to receive on item creation
# in
class CreateBase(BaseModel):
    # inherent to add more properties for creating
    pass


# Properties to receive on item update
# in
class UpdateBase(BaseModel):
    # inherent to add more properties for updating
    id: int


# Properties to receive on item delete
# in
class DeleteBase(BaseModel):
    # inherent to add more properties for deleting
    id: int
    is_deleted: Optional[bool] = True
    updated_at: Optional[str] = str(datetime.now())


# response


# Properties shared by models stored in DB
class InDBBase(BaseModel):
    id: int
    created_at: str

class InDBBaseWithoutCreatedAt(BaseModel):
    id: int


# Properties to return to client
# curd model
# out
class ResponseBase(InDBBase):
    # inherent to add more properties for responding
    table_name: ClassVar[str] = "ResponseBase".lower()
    Config: ClassVar[ConfigDict] = ConfigDict(
        extra="ignore", arbitrary_types_allowed=True
    )

class ResponseBaseWithoutCreatedAt(InDBBaseWithoutCreatedAt):
    # inherent to add more properties for responding
    table_name: ClassVar[str] = "ResponseBase".lower()
    Config: ClassVar[ConfigDict] = ConfigDict(
        extra="ignore", arbitrary_types_allowed=True
    )