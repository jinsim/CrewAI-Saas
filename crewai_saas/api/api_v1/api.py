from fastapi import APIRouter

from crewai_saas.api.api_v1.endpoints import test_items
from crewai_saas.api.api_v1.endpoints import crews, users

api_router = APIRouter()
api_router.include_router(test_items.router, prefix="/test_items", tags=["test_items"])
api_router.include_router(crews.router, prefix="/crews", tags=["crews"])
api_router.include_router(users.router, prefix="/users", tags=["users"])