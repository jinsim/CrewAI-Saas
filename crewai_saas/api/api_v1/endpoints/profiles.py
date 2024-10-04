import logging

from fastapi import APIRouter, HTTPException
from typing import Annotated
from fastapi import  Path, Depends
from starlette.responses import JSONResponse
from crewai_saas.core.google_auth_utils import GoogleAuthUtils

from crewai_saas.api.deps import SessionDep
from crewai_saas.crud import profile, country, api_key
from crewai_saas.model import Profile, ProfileCreate, ProfileUpdate, Country, ApiKey, ApiKeyCreate, ApiKeyUpdate

router = APIRouter()

@router.get("/countries")
async def read_countries(session: SessionDep) -> list[Country]:
    return await country.get_all(session)

@router.get("/profile_info")
async def read_profile_by_token(session: SessionDep,
                         profile_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> Profile | None:
    return await profile.get_active_by_email(session, email=profile_email)


@router.get("/{profile_id}")
async def read_profile_by_id(profile_id: Annotated[int, Path(title="The ID of the Profile to get")],
                          session: SessionDep) -> Profile | None:
    return await profile.get_active(session, id=profile_id)


@router.get("/")
async def read_profile(session: SessionDep) -> list[Profile]:
    return await profile.get_all_active(session)

@router.post("/")
async def create_profile(profile_in: ProfileCreate, session: SessionDep) -> Profile:
    return await profile.create(session, obj_in=profile_in)

@router.put("/{profile_id}")
async def update_profile(profile_id: Annotated[int, Path(title="The ID of the Profile to get")],
                      profile_in: ProfileUpdate,
                      session: SessionDep,
                      profile_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> Profile:
    validation_result = await validate(session, profile_id, profile_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    return await profile.update(session, obj_in=profile_in, id=profile_id)


@router.delete("/{profile_id}")
async def delete_profile(profile_id: Annotated[int, Path(title="The ID of the Profile to get")],
                      session: SessionDep,
                      profile_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> Profile:
    validation_result = await validate(session, profile_id, profile_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    return await profile.soft_delete(session, id=profile_id)




@router.post("/{profile_id}/api-keys")
async def create_api_key(profile_id: Annotated[int, Path(title="The ID of the Profile to get")],
                         api_key_in: ApiKeyCreate, session: SessionDep,
                         profile_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> ApiKey:
    validation_result = await validate(session, profile_id, profile_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    created_api_key = await api_key.create(session, obj_in=api_key_in)
    return await api_key.get(session, id=created_api_key.id)



@router.get("/{profile_id}/api-keys")
async def read_api_keys(profile_id: Annotated[int, Path(title="The ID of the Profile to get")],
                        session: SessionDep,
                        profile_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> list[ApiKey]:
    validation_result = await validate(session, profile_id, profile_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    return await api_key.get_multi_by_owner(session, profile_id)

@router.get("/{profile_id}/api-keys/by-provider-id/{llm_provider_id}")
async def read_api_keys_by_provider(profile_id: Annotated[int, Path(title="The ID of the Profile to get")],
                                    llm_provider_id: Annotated[int, Path(title="The ID of the LLMProvider to get")],
                                    session: SessionDep) -> ApiKey | None:
    return await api_key.get_by_profile_id_and_llm_provider_id(session, profile_id=profile_id, llm_provider_id=llm_provider_id)

@router.put("/{profile_id}/api-keys/{api_key_id}")
async def update_api_key(profile_id: Annotated[int, Path(title="The ID of the Profile to get")],
                         api_key_id: Annotated[int, Path(title="The ID of the ApiKey to get")],
                         api_key_in: ApiKeyUpdate, session: SessionDep,
                         profile_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> ApiKey:
    validation_result = await validate(session, profile_id, profile_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    return await api_key.update(session, obj_in=api_key_in, id=api_key_id)



@router.delete("/{profile_id}/api-keys/{api_key_id}")
async def delete_api_key(profile_id: Annotated[int, Path(title="The ID of the Profile to get")],
                         api_key_id: Annotated[int, Path(title="The ID of the ApiKey to get")],
                         session: SessionDep,
                         profile_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> ApiKey:

    await validate(session, profile_id, profile_email)
    validation_result = await validate(session, profile_id, profile_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    return await api_key.delete(session, id=api_key_id)

async def validate(session, profile_id: int, profile_email: str):
    try:
        await profile.validate_profile(session, profile_id, profile_email)
    except HTTPException as e:
        logging.warning(f"Validation failed: {e}, profile_id: {profile_id}, profile_email: {profile_email}")
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        logging.warning(f"Validation failed: {e}, profile_id: {profile_id}, profile_email: {profile_email}")
        return JSONResponse(status_code=500, content={"detail": str(e)})
    return True

async def get_profile_by_token(session: SessionDep, profile_email: str):
    return await profile.get_active_by_email(session, email=profile_email)