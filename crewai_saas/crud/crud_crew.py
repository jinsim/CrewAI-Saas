from supabase_py_async import AsyncClient

from crewai_saas.crud.base import CRUDBase
from crewai_saas.schema import Crew, CrewCreate, CrewUpdate
from crewai_saas.schema.auth import UserIn

class CRUDCrew(CRUDBase[Crew, CrewCreate, CrewUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: CrewCreate) -> Crew:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: str) -> Crew | None:
        return await super().get(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Crew]:
        return await super().get_all(db)

    async def get_multi_by_owner(self, db: AsyncClient, *, user: UserIn) -> list[Crew]:
        return await super().get_multi_by_owner(db, user=user)

    async def update(self, db: AsyncClient, *, obj_in: CrewUpdate) -> Crew:
        return await super().update(db, obj_in=obj_in)

    async def delete(self, db: AsyncClient, *, id: str) -> Crew:
        return await super().delete(db, id=id)


crew = CRUDCrew(Crew)