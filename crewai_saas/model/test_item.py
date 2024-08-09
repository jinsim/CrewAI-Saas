from typing import ClassVar

from crewai_saas.model.base import CreateBase, InDBBase, ResponseBase, UpdateBase


# request
# Properties to receive on item creation
# in
class TestItemCreate(CreateBase):
    test_data: str


# Properties to receive on item update
# in
class TestItemUpdate(UpdateBase):
    test_data: str


# Properties to return to client
# curd model
# out
class TestItem(ResponseBase):
    test_data: str

    table_name: ClassVar[str] = "test_item"


# Properties properties stored in DB
class TestItemInDB(InDBBase):
    test_data: str