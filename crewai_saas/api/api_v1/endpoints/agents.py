from fastapi import APIRouter
from typing import Annotated
from fastapi import FastAPI, Path, Query
from datetime import datetime

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import crew, task, task_context, agent, tool
from crewai_saas.schema import Crew, CrewCreate, CrewUpdate, Task, TaskCreate, TaskUpdate, TaskWithContext, Agent, AgentCreate, AgentUpdate, Tool, AgentWithTool

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

@router.patch("/{agent_id}")
async def update_agent(agent_id: Annotated[int, Path(title="The ID of the it to get")],
                       agent_in: AgentUpdate, session: SessionDep) -> Agent:
    return await agent.update(session, obj_in=agent_in, id=agent_id)

@router.delete("/{agent_id}")
async def delete_agent(agent_id: Annotated[int, Path(title="The ID of the it to get")],
                       session: SessionDep) -> Agent:
    return await agent.soft_delete(session, id=agent_id)
