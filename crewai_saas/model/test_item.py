from typing import ClassVar

from crewai_saas.model.base import CreateBase, InDBBase, ResponseBase, UpdateBase


class TestItemCreate(CreateBase):
    test_data: str

class TestItemUpdate(UpdateBase):
    test_data: str


class TestItem(ResponseBase):
    test_data: str

    table_name: ClassVar[str] = "test_item"

class TestItemInDB(InDBBase):
    test_data: str