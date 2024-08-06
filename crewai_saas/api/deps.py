
import logging
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from gotrue.errors import AuthApiError
from supabase_py_async import AsyncClient, create_client
from supabase_py_async.lib.client_options import ClientOptions

from crewai_saas.core.config import settings
from crewai_saas.model.auth import UserIn

super_client: AsyncClient | None = None


async def init_super_client() -> None:
    """for validation access_token init at life span event"""
    global super_client
    super_client = await create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
        options=ClientOptions(postgrest_client_timeout=10, storage_client_timeout=10),
    )
    # await super_client.auth.sign_in_with_password(
    #     {"email": settings.SUPERUSER_EMAIL, "password": settings.SUPERUSER_PASSWORD}
    # )


# auto get access_token from header
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="please login by supabase-js to get token"
)
AccessTokenDep = Annotated[str, Depends(reusable_oauth2)]


# 회원 인증 인가 추가 시 수정
async def get_current_user(access_token: AccessTokenDep) -> UserIn:
    """get current user from access_token and  validate same time"""
    if not super_client:
        raise HTTPException(status_code=500, detail="Super client not initialized")

    user_rsp = await super_client.auth.get_user(jwt=access_token)
    if not user_rsp:
        logging.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    return UserIn(**user_rsp.user.model_dump(), access_token=access_token)


CurrentUser = Annotated[UserIn, Depends(get_current_user)]


async def get_db_auth(user: CurrentUser) -> AsyncClient:
    client: AsyncClient | None = None
    try:
        client = await create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
            access_token=user.access_token,
            options=ClientOptions(
                postgrest_client_timeout=10, storage_client_timeout=10
            ),
        )
        # checks all done in supabase-py !
        # await client.auth.set_session(token.access_token, token.refresh_token)
        # session = await client.auth.get_session()
        yield client

    except AuthApiError as e:
        logging.error(e)
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    finally:
        if client:
            await client.auth.sign_out()

async def get_db() -> AsyncClient:
    client: AsyncClient | None = None
    try:
        client = await create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
            options=ClientOptions(
                postgrest_client_timeout=10, storage_client_timeout=10
            ),
        )
        # checks all done in supabase-py !
        yield client

    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(
            status_code=400, detail="Unknown error occurred"
        )

SessionDep = Annotated[AsyncClient, Depends(get_db)]