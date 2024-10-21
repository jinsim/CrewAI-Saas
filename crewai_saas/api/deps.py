
import logging
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from supabase._async.client import AsyncClient, create_client, ClientOptions
from crewai_saas.core.config import settings
from crewai_saas.model.auth import UserIn

super_client: AsyncClient | None = None


async def init_super_client() -> None:
    """for validation access_token init at life span event"""
    global super_client

    logging.info("Initializing super client")

    super_client = await create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
        options=ClientOptions(postgrest_client_timeout=10, storage_client_timeout=10),
    )


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="please login by supabase-js to get token"
)
AccessTokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_current_user(access_token: AccessTokenDep) -> UserIn:
    """get current user from access_token and  validate same time"""
    if not super_client:
        raise HTTPException(status_code=500, detail="Super client not initialized")

    user_rsp = super_client.auth.get_user(jwt=access_token)
    if not user_rsp:
        logging.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    return UserIn(**user_rsp.user.model_dump(), access_token=access_token)


CurrentUser = Annotated[UserIn, Depends(get_current_user)]

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

        yield client

    except Exception as e:
        logging.error(e, exc_info=True, stack_info=True)
        raise HTTPException(
            status_code=400, detail="Unknown error occurred"
        )

SessionDep = Annotated[AsyncClient, Depends(get_db)]