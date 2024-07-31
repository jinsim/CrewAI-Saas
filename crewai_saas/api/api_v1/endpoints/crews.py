from fastapi import APIRouter
from datetime import datetime

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import crew, task
from crewai_saas.schema import *

router = APIRouter()

@router.post("/")
async def create_crew(crew_in: CrewCreate, session: SessionDep) -> Crew:
    return await crew.create(session, obj_in=crew_in)

@router.put("/{crew_id}")
async def update_crew(crew_id: str, crew_in: CrewUpdate, session: SessionDep) -> Crew:
    return await crew.update(session, obj_in=crew_in)

@router.get("/")
async def read_crews(session: SessionDep) -> list[Crew]:
    return await crew.get_all_active(session)

@router.get("/{crew_id}")
async def read_crew_by_id(crew_id: str, session: SessionDep) -> Crew | None:
    return await crew.get_active(session, id=id)

@router.delete("/{crew_id}")
async def delete_crew(crew_id: str, session: SessionDep) -> Crew:
    return await crew.soft_delete(session, id=id)

# Task
@router.get("/{crew_id}/tasks")
async def read_crew_tasks(crew_id: str, session: SessionDep) -> list[Task]:
    return await task.get_all_active_by_crew_id(session, crew_id)

@router.put("/{crew_id}/tasks/{task_id}")
async def update_crew_task(crew_id: str, task_id: str, task_in: TaskUpdate, session: SessionDep) -> Task:
    return await task.update(session, obj_in=task_in)

@router.delete("/{crew_id}/tasks/{task_id}")
async def delete_crew_task(crew_id: str, task_id: str, session: SessionDep) -> Task:
    return await task.soft_delete(session, id=task_id)

@router.post("/{crew_id}/tasks")
async def create_crew_task(crew_id: str, task_in: TaskCreate, session: SessionDep) -> Task:
    return await task.create(session, obj_in=task_in)