from fastapi import APIRouter, HTTPException
from typing import Annotated
from fastapi import  Path, Depends
from starlette.responses import JSONResponse
from crewai_saas.core.google_auth_utils import GoogleAuthUtils

from crewai_saas.api.deps import SessionDep
from crewai_saas.crud import user, country, api_key
from crewai_saas.model import User, UserCreate, UserUpdate, Country, ApiKey, ApiKeyCreate, ApiKeyUpdate

router = APIRouter()

@router.get("/countries")
async def read_countries(session: SessionDep) -> list[Country]:
    return await country.get_all(session)

@router.get("/user_info")
async def read_user_by_token(session: SessionDep,
                         user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> User | None:
    return await user.get_active_by_email(session, email=user_email)


@router.get("/{user_id}")
async def read_user_by_id(user_id: Annotated[int, Path(title="The ID of the User to get")],
                          session: SessionDep) -> User | None:
    return await user.get_active(session, id=user_id)


@router.get("/")
async def read_user(session: SessionDep) -> list[User]:
    return await user.get_all_active(session)

@router.post("/")
async def create_user(user_in: UserCreate, session: SessionDep) -> User:
    return await user.create(session, obj_in=user_in)

@router.put("/{user_id}")
async def update_user(user_id: Annotated[int, Path(title="The ID of the User to get")],
                      user_in: UserUpdate,
                      session: SessionDep,
                      user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> User:
    try:
        await user.validate_user(session, user_id, user_email)
        return await user.update(session, obj_in=user_in, id=user_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

@router.delete("/{user_id}")
async def delete_user(user_id: Annotated[int, Path(title="The ID of the User to get")],
                      session: SessionDep,
                      user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> User:
    try:
        await user.validate_user(session, user_id, user_email)
        return await user.soft_delete(session, id=user_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})



@router.post("/{user_id}/api_keys")
async def create_api_key(user_id: Annotated[int, Path(title="The ID of the User to get")],
                         api_key_in: ApiKeyCreate, session: SessionDep,
                         user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> ApiKey:
    try:
        await user.validate_user(session, user_id, user_email)
        return await api_key.create(session, obj_in=api_key_in)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.get("/{user_id}/api_keys")
async def read_api_keys(user_id: Annotated[int, Path(title="The ID of the User to get")],
                        session: SessionDep,
                        user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> list[ApiKey]:
    try:
        await user.validate_user(session, user_id, user_email)
        return await api_key.get_multi_by_owner(session, user_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.put("/{user_id}/api_keys/{api_key_id}")
async def update_api_key(user_id: Annotated[int, Path(title="The ID of the User to get")],
                         api_key_id: Annotated[int, Path(title="The ID of the ApiKey to get")],
                         api_key_in: ApiKeyUpdate, session: SessionDep,
                         user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> ApiKey:
    try:
        await user.validate_user(session, user_id, user_email)
        return await api_key.update(session, obj_in=api_key_in, id=api_key_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.delete("/{user_id}/api_keys/{api_key_id}")
async def delete_api_key(user_id: Annotated[int, Path(title="The ID of the User to get")],
                         api_key_id: Annotated[int, Path(title="The ID of the ApiKey to get")],
                         session: SessionDep,
                         user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> ApiKey:
    try:
        await user.validate_user(session, user_id, user_email)
        return await api_key.delete(session, id=api_key_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


