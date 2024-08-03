from supabase_py_async import AsyncClient

from crewai_saas.crud.base import CRUDBase, ReadBase
from crewai_saas.schema import EmployedCrew, EmployedCrewCreate, EmployedCrewUpdate
from crewai_saas.schema.auth import UserIn

class CRUDEmployedCrew(CRUDBase[EmployedCrew, EmployedCrewCreate, EmployedCrewUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: EmployedCrewCreate) -> EmployedCrew:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: int) -> EmployedCrew | None:
        return await super().get(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[EmployedCrew]:
        return await super().get_all(db)

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> list[EmployedCrew]:
        return await super().get_multi_by_owner(db, user_id=user_id)

    async def update(self, db: AsyncClient, *, obj_in: EmployedCrewUpdate) -> EmployedCrew:
        return await super().update(db, obj_in=obj_in)

    async def delete(self, db: AsyncClient, *, id: int) -> EmployedCrew:
        return await super().delete(db, id=id)

empolyed_crew = CRUDEmployedCrew(EmployedCrew)