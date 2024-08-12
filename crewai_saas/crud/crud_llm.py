from supabase_py_async import AsyncClient

from crewai_saas.crud.base import CRUDBase, ReadBase
from crewai_saas.model import Llm, LlmInDB, LlmProvider, LlmProviderInDB

class ReadLlm(ReadBase[Llm]):
    async def get_all(self, db: AsyncClient) -> list[Llm]:
        return await super().get_all(db)

    async def get_all_by_provider_id(self, db: AsyncClient, provider_id: int) -> list[Llm]:
        data, count = await db.table(self.model.table_name).select("*").eq("llm_provider_id", provider_id).execute()
        _, got = data
        return [self.model(**item) for item in got]

class ReadLlmProvider(ReadBase[LlmProvider]):
    async def get_all(self, db: AsyncClient) -> list[LlmProvider]:
        return await super().get_all(db)
llm = ReadLlm(Llm)
llm_provider = ReadLlmProvider(LlmProvider)
