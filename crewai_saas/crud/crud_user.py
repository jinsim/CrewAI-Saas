from supabase_py_async import AsyncClient
from typing import Generic, TypeVar, Any, List, Optional

from crewai_saas.crud.base import CRUDBase, ReadBase
from crewai_saas.model import *
from crewai_saas.model.auth import UserIn

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: UserCreate) -> User:
        existing_user = await self.get_active_by_email(db, email=obj_in.email)

        if existing_user:
            existing_user.is_new_user = False
            return existing_user

        new_user = await super().create(db, obj_in=obj_in)
        new_user.is_new_user = True
        return new_user

    async def get(self, db: AsyncClient, *, id: int) -> User | None:
        return await super().get(db, id=id)

    async def get_active(self, db: AsyncClient, *, id: int) -> User | None:
        return await super().get_active(db, id=id)

    async def get_active_by_email(self, db: AsyncClient, *, email: str) -> User | None:
        return await super().get_active_by_email(db, email=email)

    async def get_all(self, db: AsyncClient) -> list[User]:
        return await super().get_all(db)

    async def get_all_active(self, db: AsyncClient) -> list[User]:
        return await super().get_all_active(db)

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[User]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def delete(self, db: AsyncClient, *, id: int) -> User:
        return await super().delete(db, id=id)

class ReadCountry(ReadBase[Country]):
    async def get(self, db: AsyncClient, *, id: int) -> Country | None:
        return await super().get(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Country]:
        return await super().get_all(db)

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[Country]:
        return await super().get_multi_by_owner(db, user_id=user_id)

class CRUDApiKey(CRUDBase[ApiKey, ApiKeyCreate, ApiKeyUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: ApiKeyCreate) -> ApiKey:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: int) -> ApiKey | None:
        return await super().get(db, id=id)

    async def get_active(self, db: AsyncClient, *, id: int) -> ApiKey | None:
        return await super().get_active(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[ApiKey]:
        return await super().get_all(db)

    async def get_all_active(self, db: AsyncClient) -> list[ApiKey]:
        return await super().get_all_active(db)

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[ApiKey]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def get_all_active_by_owner(self, db: AsyncClient, user_id: int) -> list[ApiKey]:
        return await super().get_all_active_by_owner(db, user_id=user_id)

    async def get_active_by_llm_provider_id(self, db: AsyncClient, *, llm_provider_id: int) -> ApiKey | None:
        return await db.table(self.model.table_name).select("*").eq("llm_provider_id", llm_provider_id).execute()
        _, got = data
        if not got:
            return None

        return [self.model(**item) for item in got][0]


    async def delete(self, db: AsyncClient, *, id: int) -> ApiKey:
        return await super().delete(db, id=id)

    async def get_active_by_user_id_and_llm(self, db: AsyncClient, *, user_id: int, llm_id: int) -> ApiKey | None:
        provider_id_response = await db.table("llm").select("llm_provider_id").eq("id", llm_id).execute()
        provider_id = provider_id_response.data[0]["llm_provider_id"]  # provider_id를 추출합니다

        data, count = await db.table(self.model.table_name).select("*").eq("user_id", user_id).eq(
            "llm_provider_id", provider_id).execute()
        _, got = data
        return self.model(**got[0]) if got else None



user = CRUDUser(User)
country = ReadCountry(Country)
api_key = CRUDApiKey(ApiKey)
