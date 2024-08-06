from fastapi import APIRouter

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import tool
from crewai_saas.model import Tool

router = APIRouter()

@router.get("/tools")
async def read_tools(session: SessionDep) -> list[Tool]:
    return await tool.get_all_active(session)