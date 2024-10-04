from fastapi import APIRouter

from crewai_saas.api.api_v1.endpoints import test_items
from crewai_saas.api.api_v1.endpoints import crews, profiles, agents, tasks, tools, llms, employed_crews

api_router = APIRouter()
api_router.include_router(test_items.router, prefix="/test_items", tags=["test_items"])
api_router.include_router(crews.router, prefix="/crews", tags=["crews"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(llms.router, prefix="/llms", tags=["llms"])
api_router.include_router(employed_crews.router, prefix="/employed_crews", tags=["employed_crews"])