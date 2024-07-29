from fastapi import APIRouter

from crewai_saas.api.api_v1.endpoints import test_items

api_router = APIRouter()
api_router.include_router(test_items.router, prefix="/test_items", tags=["test_items"])