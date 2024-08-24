from fastapi import APIRouter, Path
from typing import Annotated

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import agent, tool, task
from crewai_saas.model import Agent, AgentCreate, AgentUpdate, Tool, AgentWithTool

router = APIRouter()

@router.post("/")
async def create_agent(agent_in: AgentCreate, session: SessionDep) -> Agent:
    return await agent.create(session, obj_in=agent_in)

@router.get("/by-crew-id/{crew_id}")
async def read_agents_by_crew_id(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                                 session: SessionDep) -> list[AgentWithTool]:
    agents = await agent.get_all_active_by_crew_id(session, crew_id)
    ret = [
        AgentWithTool(**it.dict(), tools=await tool.get_all_by_ids(session, it.tool_ids))
        for it in agents
    ]
    return ret

@router.get("/by-task-id/{task_id}")
async def read_agents_by_task_id(task_id: Annotated[int, Path(title="The ID of the Task to get")],
                                 session: SessionDep) -> Agent:
    agent_by_task_id = await task.get_active(session, id=task_id)
    return await agent.get_active(session, id=agent_by_task_id.agent_id)

@router.patch("/{agent_id}")
async def update_agent(agent_id: Annotated[int, Path(title="The ID of the it to get")],
                       agent_in: AgentUpdate, session: SessionDep) -> Agent:
    return await agent.update_exclude_none(session, obj_in=agent_in, id=agent_id)

@router.delete("/{agent_id}")
async def delete_agent(agent_id: Annotated[int, Path(title="The ID of the it to get")],
                       session: SessionDep) -> Agent:
    return await agent.soft_delete(session, id=agent_id)
