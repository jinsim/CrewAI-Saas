from supabase_py_async import AsyncClient

from crewai_saas.crud.base import CRUDBase, ReadBase
from crewai_saas.schema import EmployedCrew, EmployedCrewCreate, EmployedCrewUpdate, Chat, ChatCreate, ChatUpdate, MessageCreate, Message, MessageUpdate, CycleCreate, Cycle, CycleUpdate
from crewai_saas.schema.auth import UserIn

class CRUDEmployedCrew(CRUDBase[EmployedCrew, EmployedCrewCreate, EmployedCrewUpdate]):
    pass

class CRUDChat(CRUDBase[Chat, ChatCreate, ChatUpdate]):
    # 사이클이 생길 때마다 updated_at을 갱신한다.(최신순으로 정렬)
    async def get_all_active_by_employed_crew_id(self, db: AsyncClient, *, employed_crew_id: int) -> list[Chat]:
        data, count = await db.table(self.model.table_name).select("*").eq("employed_crew_id", employed_crew_id).eq("is_deleted", False).order("updated_at", desc=True).execute()
        _, got = data
        return [self.model(**item) for item in got]

class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):
    # 사이클이 생길 때마다 updated_at을 갱신한다.(최신순으로 정렬)
    async def get_all_by_chat_id(self, db: AsyncClient, *, chat_id: int) -> list[Message]:
        data, count = await db.table(self.model.table_name).select("*").eq("chat_id", chat_id).order("id", desc=True).execute()
        _, got = data
        return [self.model(**item) for item in got]

class CRUDCycle(CRUDBase[Cycle, CycleCreate, CycleUpdate]):
    pass




employed_crew = CRUDEmployedCrew(EmployedCrew)
chat = CRUDChat(Chat)
message = CRUDMessage(Message)
cycle = CRUDCycle(Cycle)

