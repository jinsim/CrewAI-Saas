from fastapi import APIRouter, Path, UploadFile, File, Response
from typing import Annotated
from starlette.responses import JSONResponse

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.core.enum import CrewStatus
from crewai_saas.crud import agent, tool, task, crew, storage, knowledge
from crewai_saas.model import Agent, AgentCreate, AgentUpdate, Tool, AgentWithTool, KnowledgeCreate

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
    ret = await agent.update_exclude_none(session, obj_in=agent_in, id=agent_id)
    await crew.update_has_published(session, crew_id=agent_in.crew_id, has_published=False)

@router.delete("/{agent_id}")
async def delete_agent(agent_id: Annotated[int, Path(title="The ID of the it to get")],
                       session: SessionDep) -> Agent:
    return await agent.soft_delete(session, id=agent_id)


@router.post("/{agent_id}/rag")
async def create_agent_rag(
        agent_id: Annotated[int, Path(title="The ID of the it to get")],
        session: SessionDep, file: UploadFile = File(...)) -> Response:
    # Read the file content
    file_content = await file.read()

    # Upload the file to Supabase storage
    file_url = await storage.upload_file(session, file_content, file.content_type)

    # Here you would typically update your agent with the new file URL
    knowledge_in = KnowledgeCreate(
        agent_id=agent_id,
        file_path=file_url
    )
    knowledge_item = await knowledge.create(session, knowledge_in)

    return JSONResponse(
        status_code=200,
        content=knowledge_item
    )

