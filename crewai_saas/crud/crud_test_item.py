from supabase._async.client import AsyncClient

from crewai_saas.crud.base import CRUDBase
from crewai_saas.model import TestItem, TestItemCreate, TestItemUpdate


class CRUDTestItem(CRUDBase[TestItem, TestItemCreate, TestItemUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: TestItemCreate) -> TestItem:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: int) -> TestItem | None:
        return await super().get(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[TestItem]:
        return await super().get_all(db)

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[TestItem]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def delete(self, db: AsyncClient, *, id: int) -> TestItem:
        return await super().delete(db, id=id)


test_item = CRUDTestItem(TestItem)