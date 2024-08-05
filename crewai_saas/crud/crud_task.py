from supabase_py_async import AsyncClient

from crewai_saas.crud.base import CRUDBase
from crewai_saas.schema import Task, TaskCreate, TaskUpdate
from crewai_saas.schema.auth import UserIn

class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: TaskCreate) -> Task:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: int) -> Task | None:
        return await super().get(db, id=id)

    async def get_active(self, db: AsyncClient, *, id: int) -> Task | None:
        return await super().get_active(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Task]:
        return await super().get_all(db)

    async def get_all_active(self, db: AsyncClient) -> list[Task]:
        return await super().get_all_active(db)

    async def get_all_active_by_crew_id(self, db: AsyncClient, *, crew_id: int) -> list[Task]:
        data, count = await db.table(self.model.table_name).select("*").eq("crew_id", crew_id).eq("is_deleted", False).execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[Task]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def delete(self, db: AsyncClient, *, id: int) -> Task:
        return await super().delete(db, id=id)

task = CRUDTask(Task)