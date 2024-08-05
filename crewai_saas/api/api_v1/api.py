from fastapi import APIRouter

from crewai_saas.api.api_v1.endpoints import test_items
from crewai_saas.api.api_v1.endpoints import crews, users, agents, tasks, tools, llms, employed_crews, chats

api_router = APIRouter()
api_router.include_router(test_items.router, prefix="/test_items", tags=["test_items"])
api_router.include_router(crews.router, prefix="/crews", tags=["crews"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(llms.router, prefix="/llms", tags=["llms"])
api_router.include_router(employed_crews.router, prefix="/employed_crews", tags=["employed_crews"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])