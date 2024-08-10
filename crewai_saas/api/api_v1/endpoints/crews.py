from fastapi import APIRouter, Path, Response
from typing import Annotated

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import crew, employed_crew
from crewai_saas.model import Crew, CrewCreate, CrewUpdate

router = APIRouter()

@router.post("/")
async def create_crew(crew_in: CrewCreate, session: SessionDep) -> Crew:

    crew_data = await crew.create(session, obj_in=crew_in)
    await employed_crew.create_owned(session, crew_id=crew_data.id, user_id=crew_in.user_id)
    return crew_data


@router.patch("/{crew_id}")
async def update_crew(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                      crew_in: CrewUpdate, session: SessionDep) -> Crew:
    return await crew.update(session, obj_in=crew_in, id=crew_id)

@router.get("/")
async def read_crews(session: SessionDep) -> list[Crew]:
    return await crew.get_all_active(session)

@router.get("/{crew_id}")
async def read_crew_by_id(crew_id: Annotated[int, Path(title="The ID of the Crew to get")], session: SessionDep) -> Crew | None:
    return await crew.get_active(session, id=crew_id)

@router.delete("/{crew_id}")
async def delete_crew(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                      session: SessionDep) -> Crew:
    return await crew.soft_delete(session, id=crew_id)

