from fastapi import APIRouter, Path, Response, Request, Depends
from starlette.responses import JSONResponse
from typing import Annotated, Optional

from crewai_saas import crud
from crewai_saas.api.api_v1.endpoints.profiles import validate, get_profile_by_token
from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.core.enum import CrewStatus
from crewai_saas.core.google_auth_utils import GoogleAuthUtils
from crewai_saas.crud import crew, employed_crew, api_key, task, profile, published_crew, published_agent, published_task, knowledge
from crewai_saas.service import crewai, crewAiService

from crewai_saas.model import Crew, CrewCreate, CrewUpdate, CrewWithAll, PublishedCrewCreate, PublishedAgentCreate, PublishedTaskCreate, KnowledgeCreate

router = APIRouter()

@router.post("/")
async def create_crew(crew_in: CrewCreate, session: SessionDep) -> Crew:
    crew_data = await crew.create(session, obj_in=crew_in)
    await employed_crew.create_owned(session, crew_id=crew_data.id, profile_id=crew_in.profile_id)
    return crew_data


@router.patch("/{crew_id}")
async def update_crew(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                      session: SessionDep,
                      crew_in: CrewUpdate,
                      user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> Crew:
    get_crew = await crew.get_active(session, id=crew_id)
    validation_result = await validate(session, get_crew.profile_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result

    ret = await crud.crew.update_exclude_none(session, obj_in=crew_in, id=crew_id)
    await crew.update_has_published(session, crew_id=crew_id, has_published=False)
    return ret

@router.get("/")
async def read_crews(session: SessionDep) -> list[Crew]:
    return await crew.get_all_active(session)

@router.get("/me")
async def read_all_crews_by_owner_id(session: SessionDep,
                                     profile_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> list[Crew]:

    get_profile_by_email = await get_profile_by_token(session, profile_email=profile_email)
    return await crew.get_all_crews_by_owner(session, profile_id=get_profile_by_email.id)

@router.get("/users/{profile_id}")
async def read_public_crews_by_profile_id(profile_id: Annotated[int, Path(title="The ID of the Crew to get")], session: SessionDep) -> list[Crew]:
    return await crew.get_all_public_crews_by_profile_id(session, profile_id=profile_id)

@router.get("/search")
async def search_crews(search_query: str,
                       session: SessionDep) -> list[Crew]:
    return await crew.search_crews(session, search_string=search_query)

@router.get("/public")
async def read_published_crews(session: SessionDep) -> list[Crew]:
    return await crew.get_all_active_published(session)

@router.get("/{crew_id}")
async def read_crew_by_id(crew_id: Annotated[int, Path(title="The ID of the Crew to get")], session: SessionDep) -> Crew | None:
    return await crew.get_active(session, id=crew_id)

@router.get("/{crew_id}/verify")
async def verify_crew(crew_id: Annotated[int, Path(title="The ID of the Crew to get")], session: SessionDep) -> Response:
    agent_list = await crud.agent.get_all_active_by_crew_id(session, crew_id=crew_id)
    if len(agent_list) == 0:
        return JSONResponse(
            status_code=404,
            content={"message": "No agent in the crew"},
        )

    for agent in agent_list:
        task_instance = await task.get_active_by_agent_id(session, agent_id=agent.id)
        if task_instance is None:
            return JSONResponse(
                status_code=404,
                content={"message": "Agent has no task"},
            )


    get_crew = await crew.get_active(session, id=crew_id)
    if get_crew.description == "":
        return JSONResponse(
            status_code=404,
            content={"message": "Crew has no description"},
        )

    if get_crew.llm_id is None and not get_crew.is_sequential:
        return JSONResponse(
            status_code=404,
            content={"message": "Crew has no LLM ID"},
        )

    api_key_instance = await api_key.get_active_by_llm_provider_id(session, llm_provider_id=get_crew.llm_id)
    if api_key_instance is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Crew has no API Key"},
        )

    return JSONResponse(
        status_code=200,
        content={"message": "Successfully Verified Crew"},
    )

@router.get("/{crew_id}/info", description="크루 하위의 모든 정보를 반환")
async def get_char_info(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                      req: Request, session: SessionDep) -> Response:
    return await crewai.make_response(session=session, crew_id=crew_id)

@router.delete("/{crew_id}")
async def delete_crew(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                      session: SessionDep,
                      user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> Crew:
    get_crew = await crew.get_active(session, id=crew_id)
    validation_result = await validate(session, get_crew.profile_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    return await crew.soft_delete(session, id=crew_id)



@router.post("/{crew_id}/publish")
async def publish_crew(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                      session: SessionDep) -> Response:
    get_crew = await crew.get_active(session, id=crew_id)
    # validation_result = await validate(session, get_crew.profile_id, user_email)
    # if isinstance(validation_result, JSONResponse):
    #     return validation_result
    get_agents = await crud.agent.get_all_active_by_crew_id(session, crew_id=crew_id)
    publish_crew_entity = await published_crew.create(session, obj_in=PublishedCrewCreate(**get_crew.dict(), crew_id=crew_id))

    agent_dict = {}
    for agent_entity in get_agents:
        published_agent_entity = await published_agent.create(session, obj_in=PublishedAgentCreate(**agent_entity.dict(), published_crew_id=publish_crew_entity.id))
        knowledge_entities = await knowledge.get_all_active_by_agent_id(session, agent_id=agent_entity.id)
        for knowledge_entity in knowledge_entities:
            knowledge_in = KnowledgeCreate(
                published_agent_id=published_agent_entity.id,
                file_path=knowledge_entity.file_path
            )
            await knowledge.create(session, knowledge_in)

        agent_dict[agent_entity.id] = published_agent_entity

    task_dict = {}
    for task_id in get_crew.task_ids:
        task_entity = await crud.task.get_active(session, id=task_id)
        if task_entity:
            context_task_ids = []
            if task_entity.context_task_ids:
                context_task_ids = [task_dict[task_id].id for task_id in task_entity.context_task_ids]
            task_dict[task_entity.id] = await published_task.create(session, obj_in=PublishedTaskCreate(**task_entity.dict(), published_agent_id=agent_dict[task_entity.agent_id].id, published_crew_id=publish_crew_entity.id, context_published_task_ids=context_task_ids))
    await published_crew.set_published_task_ids(session, published_crew_id=publish_crew_entity.id, published_task_ids=[task_dict[task_id].id for task_id in get_crew.task_ids])
    # await crew.update_status(session, crew_id=crew_id, status=CrewStatus.PUBLIC)
    await crew.update_has_published(session, crew_id=crew_id, has_published=True)

    return await crewai.make_response(session=session, crew_id=crew_id)