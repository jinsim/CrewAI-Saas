from typing import Optional, List

from supabase_py_async import AsyncClient

from crewai_saas.core.enum import CycleStatus
from crewai_saas.crud.base import CRUDBase, ReadBase
from crewai_saas.model import EmployedCrew, EmployedCrewCreate, EmployedCrewUpdate, Chat, ChatCreate, ChatUpdate, MessageCreate, Message, MessageUpdate, CycleCreate, Cycle, CycleUpdate
from crewai_saas.model.auth import UserIn
from crewai_saas.core.enum.CycleStatus import CycleStatus

class CRUDEmployedCrew(CRUDBase[EmployedCrew, EmployedCrewCreate, EmployedCrewUpdate]):

    async def get_all_active_employed_crews_by_owner(self, db: AsyncClient, *, user_id: int) -> List[EmployedCrew]:
        query = db.table(self.model.table_name).select("*").eq("user_id", user_id).eq("is_deleted", False).order("created_at", desc=True)
        return await self._execute_multi_query(query)
    async def create_owned(self, db: AsyncClient, *, crew_id:int, user_id:int) -> EmployedCrew:
        data, count = await db.table(self.model.table_name).insert({"crew_id": crew_id, "user_id": user_id, "is_owner": True}).execute()
        _, got = data
        return self.model(**got[0])


class CRUDChat(CRUDBase[Chat, ChatCreate, ChatUpdate]):
    # 사이클이 생길 때마다 updated_at을 갱신한다.(최신순으로 정렬)
    async def get_all_active_by_employed_crew_id(self, db: AsyncClient, *, employed_crew_id: int) -> list[Chat]:
        data, count = await db.table(self.model.table_name).select("*").eq("employed_crew_id", employed_crew_id).eq("is_deleted", False).order("updated_at", desc=True).execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def update_time(self, db: AsyncClient, *, chat_id: int) -> Chat:
        data, count = await db.table(self.model.table_name).update({"updated_at": "now()"}).eq("id", chat_id).execute()
        _, got = data
        return self.model(**got[0])

class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):

    async def create(self, db: AsyncClient, *, obj_in: MessageCreate) -> Message:
        data, count = await db.table(self.model.table_name).insert(obj_in.dict()).execute()
        _, got = data
        chat_data = await chat.update_time(db, chat_id=obj_in.chat_id)
        await db.table("employed_crew").update({"updated_at": "now()"}).eq("id", chat_data.employed_crew_id).execute()
        return self.model(**got[0])

    # 사이클이 생길 때마다 updated_at을 갱신한다.(최신순으로 정렬)
    async def get_all_by_chat_id(self, db: AsyncClient, *, chat_id: int) -> list[Message]:
        data, count = await db.table(self.model.table_name).select("*").eq("chat_id", chat_id).order("id", desc=True).execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def get_all_by_cycle_id(self, db: AsyncClient, *, cycle_id: int) -> list[Message]:
        data, count = await db.table(self.model.table_name).select("*").eq("cycle_id", cycle_id).order("id", desc=False).execute()
        _, got = data
        return [self.model(**item) for item in got]

class CRUDCycle(CRUDBase[Cycle, CycleCreate, CycleUpdate]):

    async def get_all_by_chat_id(self, db: AsyncClient, *, chat_id: int) -> list[Cycle]:
        data, count = await db.table(self.model.table_name).select("*").eq("chat_id", chat_id).order("id", desc=True).execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def get_all_finished_by_chat_id(self, db: AsyncClient, *, chat_id: int) -> list[Cycle]:
        data, count = await db.table(self.model.table_name).select("*").eq("chat_id", chat_id).eq("status", CycleStatus.FINISHED.value).order("id", desc=False).execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def get_latest_by_chat_id(self, db: AsyncClient, chat_id: int) -> Optional[Cycle]:
        data, count = await db.table(self.model.table_name).select("*").eq("chat_id", chat_id).order("id",
                                                                                                     desc=True).limit(
            1).execute()
        _, got = data

        # 데이터가 없으면 None을 반환
        if not got:
            return None

        return [self.model(**item) for item in got][0]

    async def update_status(self, db: AsyncClient, *, cycle_id: int, status: CycleStatus) -> Cycle:
        data, count = await db.table(self.model.table_name).update({"status": status.value}).eq("id", cycle_id).execute()
        _, got = data
        return self.model(**got[0])


employed_crew = CRUDEmployedCrew(EmployedCrew)
chat = CRUDChat(Chat)
message = CRUDMessage(Message)
cycle = CRUDCycle(Cycle)

