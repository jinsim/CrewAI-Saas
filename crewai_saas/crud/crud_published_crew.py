from supabase_py_async import AsyncClient

from crewai_saas.core.enum import CrewStatus
from crewai_saas.crud.base import CRUDBase, UpdateSchemaType, CRDBase
from crewai_saas.model import PublishedCrew, PublishedTask, PublishedAgent, PublishedCrewCreate, PublishedTaskCreate, PublishedAgentCreate


class CRDPublishedCrew(CRDBase[PublishedCrew, PublishedCrewCreate]):
    async def get_active_by_crew_id_latest(self, db: AsyncClient, *, crew_id: int) -> PublishedCrew:
        query = db.table(self.model.table_name).select("*").eq("crew_id", crew_id).eq("is_deleted", False).order("id", desc=True).limit(1)
        return await self._execute_single_query(query)
class CRDPublishedTask(CRDBase[PublishedTask, PublishedTaskCreate]):
    pass

class CRDPublishedAgent(CRDBase[PublishedAgent, PublishedAgentCreate]):
    pass


published_crew = CRDPublishedCrew(PublishedCrew)
published_task = CRDPublishedTask(PublishedTask)
published_agent = CRDPublishedAgent(PublishedAgent)
