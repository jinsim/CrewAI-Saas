from supabase_py_async import AsyncClient

from crewai_saas.crud.base import CRUDBase
from crewai_saas.schema import TestItem, TestItemCreate, TestItemUpdate
from crewai_saas.schema.auth import UserIn


class CRUDTestItem(CRUDBase[TestItem, TestItemCreate, TestItemUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: TestItemCreate) -> TestItem:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: str) -> TestItem | None:
        return await super().get(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[TestItem]:
        return await super().get_all(db)

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[TestItem]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def update(self, db: AsyncClient, *, obj_in: TestItemUpdate) -> TestItem:
        return await super().update(db, obj_in=obj_in)

    async def delete(self, db: AsyncClient, *, id: str) -> TestItem:
        return await super().delete(db, id=id)


test_item = CRUDTestItem(TestItem)