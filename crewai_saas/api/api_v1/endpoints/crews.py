from fastapi import APIRouter, Path, Response
from starlette.responses import JSONResponse
from typing import Annotated

from crewai_saas import crud
from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import crew, api_key, task
from crewai_saas.model import Crew, CrewCreate, CrewUpdate

router = APIRouter()

@router.post("/")
async def create_crew(crew_in: CrewCreate, session: SessionDep) -> Crew:
    return await crew.create(session, obj_in=crew_in)

@router.patch("/{crew_id}")
async def update_crew(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                      crew_in: CrewUpdate, session: SessionDep) -> Crew:
    return await crew.update(session, obj_in=crew_in, id=crew_id)

@router.get("/")
async def read_crews(session: SessionDep) -> list[Crew]:
    return await crew.get_all_active(session)

@router.get("/public")
async def read_published_crews(session: SessionDep) -> list[Crew]:
    return await crew.get_all_active_published(session)

@router.get("/{crew_id}")
async def read_crew_by_id(crew_id: Annotated[int, Path(title="The ID of the Crew to get")], session: SessionDep) -> Crew | None:
    return await crew.get_active(session, id=crew_id)

@router.get("/{crew_id}/verify")
async def verify_crew(crew_id: Annotated[int, Path(title="The ID of the Crew to get")], session: SessionDep) -> Response:
    # API KEY를 입력했는지 확인
    agent_list = await crud.agent.get_all_active_by_crew_id(session, crew_id=crew_id)
    if len(agent_list) == 0:
        return JSONResponse(
            status_code=404,
            content={"message": "No agent in the crew"},
        )
        #raise CustomException(message="No agent in the crew")

    # Agent들 중 할당이 안된 Task가 있는지 확인
    for agent in agent_list:
        task_instance = await task.get_active_by_agent_id(session, agent_id=agent.id)
        if task_instance is None:
            return JSONResponse(
                status_code=404,
                content={"message": "Agent has no task"},
            )
            #raise CustomException(message="Agent has no task")

    # crew에 설명이 없는지 확인
    get_crew = await crew.get_active(session, id=crew_id)
    if get_crew.description == "":
        return JSONResponse(
            status_code=404,
            content={"message": "Crew has no description"},
        )
        #raise CustomException(message="Crew has no description")

    # crew에 LLM ID가 없는지 확인
    if get_crew.llm_id is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Crew has no LLM ID"},
        )
        #raise CustomException(message="Crew has no LLM ID")

    # crew에 API Key가 있는지 확인
    api_key_instance = await api_key.get_active_by_llm_provider_id(session, llm_provider_id=get_crew.llm_id)
    if api_key_instance is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Crew has no API Key"},
        )
       # raise CustomException(message="Crew has no API Key")
    return JSONResponse(
        status_code=200,
        content={"message": "Successfully Verified Crew"},
    )

@router.delete("/{crew_id}")
async def delete_crew(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                      session: SessionDep) -> Crew:
    return await crew.soft_delete(session, id=crew_id)


