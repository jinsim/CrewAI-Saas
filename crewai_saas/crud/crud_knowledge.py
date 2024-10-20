from supabase._async.client import AsyncClient

from crewai_saas.crud.base import CRUDBase, UpdateSchemaType, CRDBase
from crewai_saas.model import Knowledge, KnowledgeCreate

class CRDKnowledge(CRDBase[Knowledge, KnowledgeCreate]):
    async def create(self, db: AsyncClient, obj_in: KnowledgeCreate) -> Knowledge:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: int) -> Knowledge | None:
        return await super().get(db, id=id)

    async def get_active(self, db: AsyncClient, *, id: int) -> Knowledge | None:
        return await super().get_active(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Knowledge]:
        return await super().get_all(db)

    async def get_all_active_by_agent_id(self, db: AsyncClient, *, agent_id: int) -> list[Knowledge] | None:
        query = db.table(self.model.table_name).select("*").eq("agent_id", agent_id).eq("is_deleted",
                                                                                                          False)
        return await self._execute_multi_query(query)

    async def get_all_active_by_published_agent_id(self, db: AsyncClient, *, published_agent_id: int) -> list[Knowledge] | None:
        query = db.table(self.model.table_name).select("*").eq("published_agent_id", published_agent_id).eq("is_deleted",
                                                                                                          False)
        return await self._execute_multi_query(query)


    async def get_all_active(self, db: AsyncClient) -> list[Knowledge]:
        return await super().get_all_active(db)
    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[Knowledge]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def delete(self, db: AsyncClient, *, id: int) -> Knowledge:
        return await super().delete(db, id=id)

knowledge = CRDKnowledge(Knowledge)