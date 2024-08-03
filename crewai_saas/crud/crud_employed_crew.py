from supabase_py_async import AsyncClient

from crewai_saas.crud.base import CRUDBase, ReadBase
from crewai_saas.schema import EmployedCrew, EmployedCrewCreate, EmployedCrewUpdate, Chat, ChatCreate, ChatUpdate
from crewai_saas.schema.auth import UserIn

class CRUDEmployedCrew(CRUDBase[EmployedCrew, EmployedCrewCreate, EmployedCrewUpdate]):
    pass

class CRUDChat(CRUDBase[Chat, ChatCreate, ChatUpdate]):
    # 사이클이 생길 때마다 updated_at을 갱신한다.(최신순으로 정렬)
    async def get_all_active_by_employed_crew_id(self, db: AsyncClient, *, employed_crew_id: int) -> list[Chat]:
        data, count = await db.table(self.model.table_name).select("*").eq("employed_crew_id", employed_crew_id).eq("is_deleted", False).order("updated_at", desc=True).execute()
        _, got = data
        return [self.model(**item) for item in got]




empolyed_crew = CRUDEmployedCrew(EmployedCrew)
chat = CRUDChat(Chat)
