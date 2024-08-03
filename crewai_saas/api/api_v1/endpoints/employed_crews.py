from fastapi import APIRouter
from typing import Annotated
from fastapi import FastAPI, Path, Query
from datetime import datetime

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import empolyed_crew
from crewai_saas.schema import EmployedCrew, EmployedCrewCreate, EmployedCrewUpdate

router = APIRouter()

@router.post("/")
async def create_employed_crew(employed_crew_in: EmployedCrewCreate, session: SessionDep) -> EmployedCrew:
    return await empolyed_crew.create(session, obj_in=employed_crew_in)

@router.put("/{employed_crew_id}")
async def update_employed_crew(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                               employed_crew_in: EmployedCrewUpdate, session: SessionDep) -> EmployedCrew:
    return await empolyed_crew.update(session, obj_in=employed_crew_in)

@router.get("/users/{user_id}")
async def read_employed_crews(user_id: Annotated[int, Path(title="The ID of the User to get")], session: SessionDep) -> list[EmployedCrew]:
    return await empolyed_crew.get_all_active_by_owner(session, user_id=user_id)

@router.get("/{employed_crew_id}")
async def read_employed_crew_by_id(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")], session: SessionDep) -> EmployedCrew | None:
    return await empolyed_crew.get_active(session, id=employed_crew_id)

@router.delete("/{employed_crew_id}")
async def delete_employed_crew(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                      session: SessionDep) -> EmployedCrew:
    return await empolyed_crew.soft_delete(session, id=employed_crew_id)


