from fastapi import APIRouter
from datetime import datetime

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import crew
from crewai_saas.schema import Crew, CrewCreate, CrewUpdate

router = APIRouter()

@router.post("/")
async def create_crew(crew_in: CrewCreate, session: SessionDep) -> Crew:
    return await crew.create(session, obj_in=crew_in)

@router.put("/")
async def update_crew(crew_in: CrewUpdate, session: SessionDep) -> Crew:
    return await crew.update(session, obj_in=crew_in)

@router.get("/")
async def read_crews(session: SessionDep) -> list[Crew]:
    return await crew.get_all(session)

@router.get("/{id}")
async def read_crew_by_id(id: str, session: SessionDep) -> Crew | None:
    return await crew.get(session, id=id)
