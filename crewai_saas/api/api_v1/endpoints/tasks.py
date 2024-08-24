from fastapi import APIRouter, Path
from typing import Annotated

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import task, task_context
from crewai_saas.model import Task, TaskCreate, TaskUpdate, TaskWithContext

router = APIRouter()

@router.post("/")
async def create_task(task_in: TaskCreate, session: SessionDep) -> Task:
    return await task.create(session, obj_in=task_in)


@router.get("/by-crew-id/{crew_id}")
async def read_tasks_by_crew_id(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                          session: SessionDep) -> list[Task]:
    return await task.get_all_active_by_crew_id(session, crew_id)

@router.patch("/{task_id}")
async def update_task(task_id: Annotated[int, Path(title="The ID of the Task to get")],
                           task_in: TaskUpdate, session: SessionDep) -> Task:
    return await task.update_exclude_none(session, obj_in=task_in, id=task_id)

@router.delete("/{task_id}")
async def delete_task(task_id: Annotated[int, Path(title="The ID of the Task to get")],
                           session: SessionDep) -> Task:
    return await task.soft_delete(session, id=task_id)
