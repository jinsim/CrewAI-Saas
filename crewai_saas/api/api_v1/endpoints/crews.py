from fastapi import APIRouter
from datetime import datetime

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import crew, task, task_context, agent
from crewai_saas.schema import Crew, CrewCreate, CrewUpdate, Task, TaskCreate, TaskUpdate, TaskWithContext, Agent, AgentCreate, AgentUpdate

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
@router.post("/{crew_id}/tasks")
async def create_crew_task(crew_id: str, task_in: TaskCreate, session: SessionDep) -> Task:
    return await task.create(session, obj_in=task_in)

@router.get("/{crew_id}/tasks")
async def read_crew_tasks(crew_id: str, session: SessionDep) -> list[TaskWithContext]:
    task_list = await task.get_all_active_by_crew_id(session, crew_id)
    ret = []
    for it in task_list:
        task_contexts = await task_context.get_child_task_id_all_by_task_id(session, task_id=it.id)
        ret.append(TaskWithContext(**it.dict(), context=task_contexts))
    return ret

@router.put("/{crew_id}/tasks/{task_id}")
async def update_crew_task(crew_id: str, task_id: str, task_in: TaskUpdate, session: SessionDep) -> Task:
    return await task.update(session, obj_in=task_in)

@router.delete("/{crew_id}/tasks/{task_id}")
async def delete_crew_task(crew_id: str, task_id: str, session: SessionDep) -> Task:
    return await task.soft_delete(session, id=task_id)


# Agent
@router.post("/{crew_id}/tasks/{task_id}/agents")
async def create_task_agent(crew_id: str, task_id: str, agent_in: AgentCreate, session: SessionDep) -> Agent:
    return await agent.create(session, obj_in=agent_in)

@router.get("/{crew_id}/tasks/{task_id}/agents")
async def read_task_agents(crew_id: str, task_id: str, session: SessionDep) -> list[Agent]:
    return await agent.get_all_by_task_id(session, task_id)

@router.put("/{crew_id}/tasks/{task_id}/agents/{agent_id}")
async def update_task_agent(crew_id: str, task_id: str, agent_id: str, agent_in: AgentUpdate, session: SessionDep) -> Agent:
    return await agent.update(session, obj_in=agent_in)

@router.delete("/{crew_id}/tasks/{task_id}/agents/{agent_id}")
async def delete_task_agent(crew_id: str, task_id: str, agent_id: str, session: SessionDep) -> Agent:
    return await agent.soft_delete(session, id=agent_id)
