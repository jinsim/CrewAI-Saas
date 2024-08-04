from supabase_py_async import AsyncClient

from crewai_saas.crud.base import CRUDBase
from crewai_saas.schema import *
from crewai_saas.schema.auth import UserIn

class CRUDCrew(CRUDBase[Crew, CrewCreate, CrewUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: CrewCreate) -> Crew:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: int) -> Crew | None:
        return await super().get(db, id=id)

    async def get_active(self, db: AsyncClient, *, id: int) -> Crew | None:
        return await super().get_active(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Crew]:
        return await super().get_all(db)

    async def get_all_active(self, db: AsyncClient) -> list[Crew]:
        return await super().get_all_active(db)

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[Crew]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def delete(self, db: AsyncClient, *, id: int) -> Crew:
        return await super().delete(db, id=id)

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

    async def get_all_active_by_crew_id(self, db: AsyncClient, crew_id: int) -> list[Task]:
        data, count = await db.table(self.model.table_name).select("*").eq("crew_id", crew_id).eq("is_deleted", False).execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[Task]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def delete(self, db: AsyncClient, *, id: int) -> Task:
        return await super().delete(db, id=id)

class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: AgentCreate) -> Agent:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: int) -> Agent | None:
        return await super().get(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Agent]:
        return await super().get_all(db)

    async def get_all_with_too_by_task_id(self, db: AsyncClient, task_id: int) -> list[AgentWithTool]:
        data, count = await db.table(self.model.table_name).select("*").eq("task_id", task_id).execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[Agent]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def delete(self, db: AsyncClient, *, id: int) -> Agent:
        return await super().delete(db, id=id)

class CRUDTaskContext(CRUDBase[TaskContext, TaskContextCreate, TaskContextUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: TaskContextCreate) -> TaskContext:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: int) -> TaskContext | None:
        return await super().get(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[TaskContext]:
        return await super().get_all(db)

    async def get_child_task_id_all_by_task_id(self, db: AsyncClient, task_id: int) -> list[str]:
        data, count = await db.table(self.model.table_name).select("child_task_id").eq("parent_task_id", task_id).execute()
        _, got = data
        return [item["child_task_id"] for item in got]

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[TaskContext]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def delete(self, db: AsyncClient, *, id: int) -> TaskContext:
        return await super().delete(db, id=id)


class CRUDTool(CRUDBase[Tool, ToolCreate, ToolUpdate]):
    async def get(self, db: AsyncClient, *, id: int) -> Tool | None:
        return await super().get(db, id=id)

    async def get_active(self, db: AsyncClient, *, id: int) -> Tool | None:
        return await super().get_active(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Tool]:
        return await super().get_all(db)

    async def get_all_active(self, db: AsyncClient) -> list[Tool]:
        return await super().get_all_active(db)

    async def get_all_by_ids(self, db: AsyncClient, ids: list) -> list[Tool]:
        data, count = await db.table(self.model.table_name).select("*").in_("id", ids).execute()
        _, got = data
        return [self.model(**item) for item in got]


crew = CRUDCrew(Crew)
task = CRUDTask(Task)
task_context = CRUDTaskContext(TaskContext)
agent = CRUDAgent(Agent)
tool = CRUDTool(Tool)