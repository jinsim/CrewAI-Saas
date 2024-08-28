from supabase_py_async import AsyncClient

from typing import List
from crewai_saas.core.enum import CrewStatus
from crewai_saas.crud.base import CRUDBase, UpdateSchemaType
from crewai_saas.model import Crew, Task, Agent, Tool, TaskContext, CrewCreate, CrewUpdate, TaskCreate, TaskUpdate, AgentCreate, AgentUpdate, TaskContextCreate, TaskContextUpdate, ToolCreate, ToolUpdate

class CRUDCrew(CRUDBase[Crew, CrewCreate, CrewUpdate]):

    async def get(self, db: AsyncClient, *, id: int) -> Crew | None:
        return await super().get(db, id=id)

    async def get_active(self, db: AsyncClient, *, id: int) -> Crew | None:
        return await super().get_active(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Crew]:
        return await super().get_all(db)

    async def get_all_active(self, db: AsyncClient) -> list[Crew]:
        return await super().get_all_active(db)

    async def get_all_active_published(self, db: AsyncClient) -> list[Crew]:
        data, count = await db.table(self.model.table_name).select("*").eq("status", CrewStatus.PUBLIC.value).eq("is_deleted",
                                                                                                  False).order("updated_at", desc=True).execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def search_crews(self, db: AsyncClient, *, search_string: str) -> List[Crew]:
        filter_conditions = f"name.ilike.%{search_string}%,description.ilike.%{search_string}%"

        response = await db.table(self.model.table_name) \
            .select("*") \
            .or_(filter_conditions) \
            .eq("status", CrewStatus.PUBLIC.value) \
            .order("updated_at", desc=True) \
            .execute()

        got = response.data
        return [self.model(**item) for item in got]

    async def get_all_public_crews_by_user_id(self, db: AsyncClient, *, user_id: int) -> list[Crew]:
        data, count = await db.table(self.model.table_name).select("*").eq("user_id", user_id).eq("status", CrewStatus.PUBLIC.value).eq("is_deleted",
                                                                                                           False).order(
            "updated_at", desc=True).execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def get_all_crews_by_owner(self, db: AsyncClient, *, user_id: int) -> list[Crew]:
        print(user_id)
        data, count = await db.table(self.model.table_name).select("*").eq("user_id", user_id).eq("is_deleted",
                                                                                                           False).order(
            "updated_at", desc=True).execute()
        _, got = data
        return [self.model(**item) for item in got]



    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[Crew]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def delete(self, db: AsyncClient, *, id: int) -> Crew:
        return await super().delete(db, id=id)

    async def plus_usage(self, db: AsyncClient, *, id: int, usage: int) -> Crew:
        data, count = await db.table(self.model.table_name).update({"usage": usage+1}).eq("id", id).execute()
        _, updated = data
        return self.model(**updated[0])

    async def update(self, db: AsyncClient, *, obj_in: UpdateSchemaType, id: int) -> Crew:
        update_data = {k: v for k, v in obj_in.model_dump().items() if v is not None}
        data, _ = await db.table(self.model.table_name).update(update_data).eq("id", id).execute()
        _, updated = data
        return self.model(**updated[0])

    async def update_status(self, db: AsyncClient, *, crew_id: int, status: CrewStatus) -> Crew:
        data, _ = await db.table(self.model.table_name).update({"status": status.value}).eq("id", crew_id).execute()
        _, updated = data
        return self.model(**updated[0])

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
    async def get_active_by_agent_id(self, db : AsyncClient, agent_id: int) -> Task | None:
        data, count = await db.table(self.model.table_name).select("*").eq("agent_id", agent_id).eq("is_deleted", False).execute()
        _, got = data
        if len(got) == 0:
            return None
        return self.model(**got[0])

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

    async def get_all_active_by_crew_id(self, db: AsyncClient, crew_id: int) -> list[Agent]:
        data, count = await db.table(self.model.table_name).select("*").eq("crew_id", crew_id).eq("is_deleted", False).execute()
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