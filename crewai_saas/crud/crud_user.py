from supabase_py_async import AsyncClient
from typing import Generic, TypeVar, Any, List, Optional

from crewai_saas.crud.base import CRUDBase, ReadBase
from crewai_saas.schema import *
from crewai_saas.schema.auth import UserIn

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: UserCreate) -> User:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: int) -> User | None:
        return await super().get(db, id=id)

    async def get_active(self, db: AsyncClient, *, id: int) -> User | None:
        return await super().get_active(db, id=id)

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

    async def delete(self, db: AsyncClient, *, id: int) -> ApiKey:
        return await super().delete(db, id=id)


user = CRUDUser(User)
country = ReadCountry(Country)
api_key = CRUDApiKey(ApiKey)
