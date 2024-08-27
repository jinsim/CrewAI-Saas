from supabase_py_async import AsyncClient

from crewai_saas.core.enum import CrewStatus
from crewai_saas.crud.base import CRUDBase, UpdateSchemaType, CRDBase
from crewai_saas.model import PublishedCrew, PublishedTask, PublishedAgent, PublishedCrewCreate, PublishedTaskCreate, PublishedAgentCreate


class CRDPublishedCrew(CRDBase[PublishedCrew, PublishedCrewCreate]):
    pass
class CRDPublishedTask(CRDBase[PublishedTask, PublishedTaskCreate]):
    pass

class CRDPublishedAgent(CRDBase[PublishedAgent, PublishedAgentCreate]):
    pass


published_crew = CRDPublishedCrew(PublishedCrew)
published_task = CRDPublishedTask(PublishedTask)
published_agent = CRDPublishedAgent(PublishedAgent)
