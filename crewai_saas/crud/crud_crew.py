from supabase_py_async import AsyncClient

from crewai_saas.crud.base import CRUDBase
from crewai_saas.schema import *
from crewai_saas.schema.auth import UserIn

class CRUDCrew(CRUDBase[Crew, CrewCreate, CrewUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: CrewCreate) -> Crew:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: str) -> Crew | None:
        return await super().get(db, id=id)

    async def get_active(self, db: AsyncClient, *, id: str) -> Crew | None:
        return await super().get_active(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Crew]:
        return await super().get_all(db)

    async def get_all_active(self, db: AsyncClient) -> list[Crew]:
        return await super().get_all_active(db)

    async def get_multi_by_owner(self, db: AsyncClient, *, user: UserIn) -> list[Crew]:
        return await super().get_multi_by_owner(db, user=user)

    async def update(self, db: AsyncClient, *, obj_in: CrewUpdate) -> Crew:
        return await super().update(db, obj_in=obj_in)

    async def delete(self, db: AsyncClient, *, id: str) -> Crew:
        return await super().delete(db, id=id)

class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: TaskCreate) -> Task:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: str) -> Task | None:
        return await super().get(db, id=id)

    async def get_active(self, db: AsyncClient, *, id: str) -> Task | None:
        return await super().get_active(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Task]:
        return await super().get_all(db)

    async def get_all_active(self, db: AsyncClient) -> list[Task]:
        return await super().get_all_active(db)

    async def get_all_active_by_crew_id(self, db: AsyncClient, crew_id: str) -> list[Task]:
        data, count = await db.table(self.model.table_name).select("*").eq("crew_id", crew_id).eq("is_deleted", False).execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def get_multi_by_owner(self, db: AsyncClient, *, user: UserIn) -> list[Task]:
        return await super().get_multi_by_owner(db, user=user)

    async def update(self, db: AsyncClient, *, obj_in: TaskUpdate) -> Task:
        return await super().update(db, obj_in=obj_in)

    async def delete(self, db: AsyncClient, *, id: str) -> Task:
        return await super().delete(db, id=id)

class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: AgentCreate) -> Agent:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: str) -> Agent | None:
        return await super().get(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Agent]:
        return await super().get_all(db)

    async def get_all_by_task_id(self, db: AsyncClient, task_id: str) -> list[Agent]:
        data, count = await db.table(self.model.table_name).select("*").eq("task_id", task_id).execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def get_multi_by_owner(self, db: AsyncClient, *, user: UserIn) -> list[Agent]:
        return await super().get_multi_by_owner(db, user=user)

    async def update(self, db: AsyncClient, *, obj_in: AgentUpdate) -> Agent:
        return await super().update(db, obj_in=obj_in)

    async def delete(self, db: AsyncClient, *, id: str) -> Agent:
        return await super().delete(db, id=id)

class CRUDTaskContext(CRUDBase[TaskContext, TaskContextCreate, TaskContextUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: TaskContextCreate) -> TaskContext:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: str) -> TaskContext | None:
        return await super().get(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[TaskContext]:
        return await super().get_all(db)

    async def get_child_task_id_all_by_task_id(self, db: AsyncClient, task_id: str) -> list[str]:
        data, count = await db.table(self.model.table_name).select("child_task_id").eq("parent_task_id", task_id).execute()
        _, got = data
        return [item["child_task_id"] for item in got]

    async def get_multi_by_owner(self, db: AsyncClient, *, user: UserIn) -> list[TaskContext]:
        return await super().get_multi_by_owner(db, user=user)

    async def update(self, db: AsyncClient, *, obj_in: TaskContextUpdate) -> TaskContext:
        return await super().update(db, obj_in=obj_in)

    async def delete(self, db: AsyncClient, *, id: str) -> TaskContext:
        return await super().delete(db, id=id)

crew = CRUDCrew(Crew)
task = CRUDTask(Task)
task_context = CRUDTaskContext(TaskContext)
agent = CRUDAgent(Agent)