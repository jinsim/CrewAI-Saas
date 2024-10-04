from typing import List
from fastapi import HTTPException
from supabase_py_async import AsyncClient

from crewai_saas.core.cryptographyUtils import utils
from crewai_saas.crud.base import CRUDBase, ReadBase
from crewai_saas.model import *

class CRUDProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: ProfileCreate) -> Profile:
        existing_profile = await self.get_active_by_email(db, email=obj_in.email)

        if existing_profile:
            existing_profile.is_new_profile = False
            return existing_profile

        new_profile = await super().create(db, obj_in=obj_in)
        new_profile.is_new_profile = True
        return new_profile

    async def get(self, db: AsyncClient, *, id: int) -> Profile | None:
        return await super().get(db, id=id)

    async def get_active(self, db: AsyncClient, *, id: int) -> Profile | None:
        return await super().get_active(db, id=id)

    async def get_active_by_email(self, db: AsyncClient, *, email: str) -> Profile | None:
        return await super().get_active_by_email(db, email=email)

    async def get_all(self, db: AsyncClient) -> list[Profile]:
        return await super().get_all(db)

    async def get_all_active(self, db: AsyncClient) -> list[Profile]:
        return await super().get_all_active(db)

    async def get_multi_by_owner(self, db: AsyncClient, profile_id: int) -> list[Profile]:
        return await super().get_multi_by_owner(db, profile_id=profile_id)

    async def delete(self, db: AsyncClient, *, id: int) -> Profile:
        return await super().delete(db, id=id)

    async def validate_profile(self, db: AsyncClient, profile_id: int, profile_email: str) -> Profile:
        get_profile = await super().get_active(db, id=profile_id)
        get_profile_by_email = await super().get_active_by_email(db, email=profile_email)
        if get_profile is None or get_profile_by_email is None:
            raise HTTPException(status_code=404, detail="Profile not found.")
        if get_profile.email != profile_email:
            raise HTTPException(status_code=403, detail="Profile ID does not match the token information.")
        return get_profile


class ReadCountry(ReadBase[Country]):
    async def get(self, db: AsyncClient, *, id: int) -> Country | None:
        return await super().get(db, id=id)

    async def get_all(self, db: AsyncClient) -> list[Country]:
        return await super().get_all(db)

    async def get_multi_by_owner(self, db: AsyncClient, profile_id: int) -> list[Country]:
        return await super().get_multi_by_owner(db, profile_id=profile_id)

class CRUDApiKey(CRUDBase[ApiKey, ApiKeyCreate, ApiKeyUpdate]):
    async def create(self, db: AsyncClient, *, obj_in: ApiKeyCreate) -> ApiKey:
        obj_in.value = utils.encrypt(obj_in.value)
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncClient, *, id: int) -> ApiKey | None:
        api_key = await super().get(db, id=id)
        decrypted_api_key = utils.decrypt(api_key.value)
        api_key.value = decrypted_api_key
        return api_key
    async def get_active(self, db: AsyncClient, *, id: int) -> ApiKey | None:
        api_key = await super().get_active(db, id=id)
        decrypted_api_key = utils.decrypt(api_key.value)
        api_key.value = decrypted_api_key
        return api_key

    async def get_all(self, db: AsyncClient) -> list[ApiKey]:
        api_keys = await super().get_all(db)
        return [
            ApiKey(**{**api_key.dict(), 'value': utils.decrypt(api_key.value)})
            for api_key in api_keys
        ]

    async def get_all_active(self, db: AsyncClient) -> list[ApiKey]:
        api_keys= await super().get_all_active(db)
        return [
            ApiKey(**{**api_key.dict(), 'value': utils.decrypt(api_key.value)})
            for api_key in api_keys
        ]

    async def get_multi_by_owner(self, db: AsyncClient, profile_id: int) -> List[ApiKey]:
        api_keys = await super().get_multi_by_owner(db, profile_id=profile_id)

        return [
            ApiKey(**{**api_key.dict(), 'value': utils.decrypt(api_key.value)})
            for api_key in api_keys
        ]

    async def get_all_active_by_owner(self, db: AsyncClient, profile_id: int) -> list[ApiKey]:
        api_keys = await super().get_all_active_by_owner(db, profile_id=profile_id)
        return [
            ApiKey(**{**api_key.dict(), 'value': utils.decrypt(api_key.value)})
            for api_key in api_keys
        ]

    async def get_active_by_llm_provider_id(self, db: AsyncClient, *, llm_provider_id: int) -> ApiKey | None:
        return await db.table(self.model.table_name).select("*").eq("llm_provider_id", llm_provider_id).execute()
        _, got = data
        if not got:
            return None

        return [self.model(**item) for item in got][0]

    async def get_by_profile_id_and_llm_provider_id(self, db: AsyncClient, *, profile_id: int, llm_provider_id: int) -> ApiKey | None:
        data, count = await db.table(self.model.table_name).select("*").eq("profile_id", profile_id).eq("llm_provider_id", llm_provider_id).execute()
        _, got = data
        if not got:
            return None

        decrypted_api_key = utils.decrypt(self.model(**got[0]).value)
        return self.model(**got[0]).copy(update={"value": decrypted_api_key})

    async def delete(self, db: AsyncClient, *, id: int) -> ApiKey:
        return await super().delete(db, id=id)

    async def get_active_by_profile_id_and_llm(self, db: AsyncClient, *, profile_id: int, llm_id: int) -> ApiKey | None:
        provider_id_response = await db.table("llm").select("llm_provider_id").eq("id", llm_id).execute()
        provider_id = provider_id_response.data[0]["llm_provider_id"]

        data, count = await db.table(self.model.table_name).select("*").eq("profile_id", profile_id).eq("llm_provider_id",
                                                                                                  provider_id).execute()
        _, got = data
        if not got:
            return None

        decrypted_api_key = utils.decrypt(self.model(**got[0]).value)
        return self.model(**got[0]).copy(update={"value": decrypted_api_key})



profile = CRUDProfile(Profile)
country = ReadCountry(Country)
api_key = CRUDApiKey(ApiKey)
