from fastapi import APIRouter
from typing import Annotated
from fastapi import FastAPI, Path, Query
from datetime import datetime

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import user, country, api_key
from crewai_saas.schema import User, UserCreate, UserUpdate, Country, ApiKey, ApiKeyCreate, ApiKeyUpdate

router = APIRouter()

# Distinct Route Paths. Country 을 앞에 둔다.
# 모든 Country 을 가져오는 API
# 앞에 /users 붙일 필요는 없지만, 따로 빼기 귀찮아서 둠. 나중에 수정 필요.
@router.get("/countries")
async def read_countries(session: SessionDep) -> list[Country]:
    return await country.get_all(session)

@router.get("/")
async def read_user(session: SessionDep) -> list[User]:
    return await user.get_all_active(session)

@router.post("/")
async def create_user(user_in: UserCreate, session: SessionDep) -> User:
    return await user.create(session, obj_in=user_in)

@router.put("/{user_id}")
async def update_user(user_id: Annotated[int, Path(title="The ID of the User to get")],
                      user_in: UserUpdate, session: SessionDep) -> User:
    return await user.update(session, obj_in=user_in)

@router.get("/{user_id}")
async def read_user_by_id(user_id: Annotated[int, Path(title="The ID of the User to get")],
                          session: SessionDep) -> User | None:
    return await user.get_active(session, id=user_id)

@router.delete("/{user_id}")
async def delete_user(user_id: Annotated[int, Path(title="The ID of the User to get")],
                      session: SessionDep) -> User:
    return await user.soft_delete(session, id=user_id)

@router.post("/{user_id}/api_keys")
async def create_api_key(user_id: Annotated[int, Path(title="The ID of the User to get")],
                         api_key_in: ApiKeyCreate, session: SessionDep) -> ApiKey:
    return await api_key.create(session, obj_in=api_key_in)

@router.get("/{user_id}/api_keys")
async def read_api_keys(user_id: Annotated[int, Path(title="The ID of the User to get")],
                        session: SessionDep) -> list[ApiKey]:
    return await api_key.get_multi_by_owner(session, user_id)

@router.put("/{user_id}/api_keys/{api_key_id}")
async def update_api_key(user_id: Annotated[int, Path(title="The ID of the User to get")],
                         api_key_id: Annotated[int, Path(title="The ID of the ApiKey to get")],
                         api_key_in: ApiKeyUpdate, session: SessionDep) -> ApiKey:
    return await api_key.update(session, obj_in=api_key_in)

@router.delete("/{user_id}/api_keys/{api_key_id}")
async def delete_api_key(user_id: Annotated[int, Path(title="The ID of the User to get")],
                         api_key_id: Annotated[int, Path(title="The ID of the ApiKey to get")],
                         session: SessionDep) -> ApiKey:
    return await api_key.delete(session, id=api_key_id)


