from supabase._async.client import AsyncClient

from crewai_saas.core.enum import CrewStatus
from crewai_saas.crud.base import CRUDBase, UpdateSchemaType, CRDBase
from crewai_saas.model import PublishedCrew, PublishedTask, PublishedAgent, PublishedCrewCreate, PublishedTaskCreate, PublishedAgentCreate


class CRDPublishedCrew(CRDBase[PublishedCrew, PublishedCrewCreate]):
    async def get_active_by_crew_id_latest(self, db: AsyncClient, *, crew_id: int) -> PublishedCrew:
        query = db.table(self.model.table_name).select("*").eq("crew_id", crew_id).eq("status", CrewStatus.PUBLIC.value).eq("is_deleted", False).order("id", desc=True).limit(1)
        return await self._execute_single_query(query)

    async def set_published_task_ids(self, db: AsyncClient, *, published_crew_id: int, published_task_ids: list[int]) -> PublishedCrew:
        data, _ = await db.table(self.model.table_name).update({"published_task_ids": published_task_ids}).eq("id", published_crew_id).execute()
        _, updated = data
        return self.model(**updated[0])

class CRDPublishedTask(CRDBase[PublishedTask, PublishedTaskCreate]):
    async def get_all_active_by_published_crew_id(self, db: AsyncClient, *, published_crew_id: int) -> list[PublishedTask]:
        query = db.table(self.model.table_name).select("*").eq("published_crew_id", published_crew_id).eq("is_deleted", False)
        return await self._execute_multi_query(query)

class CRDPublishedAgent(CRDBase[PublishedAgent, PublishedAgentCreate]):
    async def get_all_active_by_published_crew_id(self, db: AsyncClient, *, published_crew_id: int) -> list[PublishedAgent]:
        query = db.table(self.model.table_name).select("*").eq("published_crew_id", published_crew_id).eq("is_deleted", False)
        return await self._execute_multi_query(query)


published_crew = CRDPublishedCrew(PublishedCrew)
published_task = CRDPublishedTask(PublishedTask)
published_agent = CRDPublishedAgent(PublishedAgent)
