from typing import Generic, TypeVar, Any, List, Optional
from supabase_py_async import AsyncClient
from crewai_saas.model.auth import UserIn
from crewai_saas.model.base import CreateBase, ResponseBase, UpdateBase, DeleteBase

ModelType = TypeVar("ModelType", bound=ResponseBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=CreateBase)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=UpdateBase)
DeleteSchemaType = TypeVar("DeleteSchemaType", bound=DeleteBase)


class ObjectNotFoundException(Exception):
    def __init__(self, id: int):
        super().__init__(f"Object with id {id} does not exist.")
        self.id = id

class ReadBase(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def _execute_multi_query(self, query: Any) -> List[ModelType]:
        data, _ = await query.execute()
        _, got = data
        return [self.model(**item) for item in got]

    async def _execute_single_query(self, query: Any) -> Optional[ModelType]:
        data, _ = await query.execute()
        _, got = data
        return self.model(**got[0]) if got else None

    async def get(self, db: AsyncClient, *, id: int) -> Optional[ModelType]:
        query = db.table(self.model.table_name).select("*").eq("id", id)
        return await self._execute_single_query(query)

    async def get_active(self, db: AsyncClient, *, id: int) -> Optional[ModelType]:
        query = db.table(self.model.table_name).select("*").eq("id", id).eq("is_deleted", False)
        return await self._execute_single_query(query)

    async def get_all(self, db: AsyncClient) -> List[ModelType]:
        query = db.table(self.model.table_name).select("*")
        return await self._execute_multi_query(query)

    async def get_all_active(self, db: AsyncClient) -> List[ModelType]:
        query = db.table(self.model.table_name).select("*").eq("is_deleted", False)
        return await self._execute_multi_query(query)

    async def get_multi_by_owner(self, db: AsyncClient, user_id: int) -> List[ModelType]:
        query = db.table(self.model.table_name).select("*").eq("user_id", user_id)
        return await self._execute_multi_query(query)

    async def get_all_active_by_owner(self, db: AsyncClient, *, user_id: int) -> List[ModelType]:
        query = db.table(self.model.table_name).select("*").eq("user_id", user_id).eq("is_deleted", False)
        return await self._execute_multi_query(query)


class CRUDBase(ReadBase[ModelType], Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    async def create(self, db: AsyncClient, *, obj_in: CreateSchemaType) -> ModelType:
        data, _ = await db.table(self.model.table_name).insert(obj_in.model_dump()).execute()
        _, created = data
        return self.model(**created[0])

    async def update(self, db: AsyncClient, *, obj_in: UpdateSchemaType, id: int) -> ModelType:
        data, _ = await db.table(self.model.table_name).update(obj_in.model_dump()).eq("id", id).execute()
        _, updated = data
        return self.model(**updated[0])

    async def delete(self, db: AsyncClient, *, id: int) -> ModelType:
        data, _ = await db.table(self.model.table_name).delete().eq("id", id).execute()
        _, deleted = data
        return self.model(**deleted[0])

    async def soft_delete(self, db: AsyncClient, *, id: int) -> ModelType:
        obj_in: DeleteSchemaType = DeleteBase(id=id)
        data, _ = await db.table(self.model.table_name).update(obj_in.model_dump()).eq("id", obj_in.id).execute()
        _, updated = data
        try:
            return self.model(**updated[0])
        except IndexError:
            raise ObjectNotFoundException(id)