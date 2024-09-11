import logging

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from fastapi import FastAPI, Path, Query, Request, Response
from datetime import datetime

from starlette.responses import JSONResponse

from crewai_saas.api.api_v1.endpoints.users import validate
from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas import crud
from crewai_saas.core.google_auth_utils import GoogleAuthUtils
from crewai_saas.model import *
from crewai_saas.service import crewai, crewAiService
from crewai_saas.tool import function_map
from crewai_saas.core.enum import CycleStatus, MessageRole, CrewStatus

router = APIRouter()

@router.get("/test")
async def test(session: SessionDep) -> Response:
    news = function_map["search_news"].invoke("NVDA")
    print(news)
    return Response(content="Success")

@router.post("/")
async def create_employed_crew(employed_crew_in: EmployedCrewCreate, session: SessionDep,user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> EmployedCrewWithCrew:
    logging.info(f"Creating employed_crew: {employed_crew_in}, user_email: {user_email}, user_id: {employed_crew_in.user_id}")
    validation_result = await validate(session, employed_crew_in.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    crew = await crud.crew.get_active(session, id=employed_crew_in.crew_id)
    crew = await crud.crew.plus_usage(session, id=employed_crew_in.crew_id, usage=crew.usage)
    employed_crew = await crud.employed_crew.create(session, obj_in=employed_crew_in)
    published_crew = await crud.published_crew.get_active_by_crew_id_latest(session, crew_id=employed_crew.crew_id)
    return EmployedCrewWithCrew(**employed_crew.dict(), published_crew=published_crew)

@router.put("/{employed_crew_id}")
async def update_employed_crew(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                               employed_crew_in: EmployedCrewUpdate, session: SessionDep,
                               user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> EmployedCrew:
    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    return await crud.employed_crew.update(session, obj_in=employed_crew_in, id=employed_crew_id)



@router.get("/by-user-id/{user_id}")
async def read_employed_crews(user_id: Annotated[int, Path(title="The ID of the User to get")], session: SessionDep,user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> list[EmployedCrew]:
    validation_result = await validate(session, user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    return await crud.employed_crew.get_all_active_by_owner(session, user_id=user_id)


@router.get("/by-user")
async def read_employed_crews_by_user(session: SessionDep
                              , user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> list[EmployedCrewWithCrew]:
    user = await crud.user.get_active_by_email(session, email=user_email)

    employed_crews = await crud.employed_crew.get_all_active_employed_crews_by_owner(session, user_id=user.id)

    results = []

    for employed_crew in employed_crews:
        published_crew = await crud.published_crew.get_active_by_crew_id_latest(session, crew_id=employed_crew.crew_id)
        if published_crew:
            results.append(EmployedCrewWithCrew(**employed_crew.dict(), published_crew=published_crew))
        else:
            logging.error(f"Published crew not found. employed_crew_id: {employed_crew.id}")

    return results

@router.get("/by-crew-id/{crew_id}")
async def read_employed_crews_by_crew_id(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                                         session: SessionDep, user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> list[EmployedCrew]:
    user_entity = await crud.user.get_active_by_email(session, email=user_email)
    return await crud.employed_crew.get_all_active_by_crew_id_and_user_id(session, crew_id=crew_id, user_id=user_entity.id)

@router.get("/is_owned/by-crew-id/{crew_id}")
async def read_owned_employed_crews_by_crew_id(crew_id: Annotated[int, Path(title="The ID of the Crew to get")],
                                         session: SessionDep, user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> EmployedCrew:
    user_entity = await crud.user.get_active_by_email(session, email=user_email)
    return await crud.employed_crew.get_active_is_owned_by_crew_id_and_user_id(session, crew_id=crew_id, user_id=user_entity.id)


@router.get("/{employed_crew_id}")
async def read_employed_crew_by_id(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")], session: SessionDep) -> EmployedCrewWithCrew | None:

    employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    published_crew = await crud.published_crew.get_active_by_crew_id_latest(session, crew_id=employed_crew.crew_id)
    return EmployedCrewWithCrew(**employed_crew.dict(), published_crew=published_crew)


@router.delete("/{employed_crew_id}")
async def delete_employed_crew(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                               session: SessionDep,
                               user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> EmployedCrew:

    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result

    return await crud.employed_crew.soft_delete(session, id=employed_crew_id)


@router.post("/{employed_crew_id}/chats/start")
async def create_chat_with_pre_questions(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                         messages_in: list[MessageRequest], session: SessionDep, user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> ChatWithCycle:
    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    chat = await crud.chat.create(session, obj_in=ChatCreate(employed_crew_id=employed_crew_id))
    cycle = await crud.cycle.create(session, obj_in=CycleCreate(chat_id=chat.id))
    message_dtos = []
    for message in messages_in:
        msg = await crud.message.create(
            session,
            obj_in=MessageCreate(cycle_id=cycle.id, **message.dict(), chat_id=chat.id)
        )
        message_dtos.append(MessageSimple(**msg.dict()))
    cycle = await crud.cycle.update(session, obj_in=CycleUpdateStatus(id=cycle.id, status=CycleStatus.FINISHED.value), id=cycle.id)
    cycle_with_messages = CycleWithMessage(**cycle.dict(), messages=message_dtos)
    chat_with_all = ChatWithCycle(**chat.dict(), cycle=cycle_with_messages)
    return chat_with_all


@router.get("/{employed_crew_id}/chats")
async def read_chats(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")], session: SessionDep, user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> list[Chat]:
    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    return await crud.chat.get_all_active_by_employed_crew_id(session, employed_crew_id=employed_crew_id)

# @router.get("/{employed_crew_id}/chats/{chat_id}/finished", description="채팅방 하위 모든 정보 (finished 된 사이클만)")
# async def read_chat_info_finished(chat_id: Annotated[int, Path(title="The ID of the Chat to get")],
#                     employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
#                     session: SessionDep,
#                     user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> ChatWithCycleList | None:
#     get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
#     validation_result = await validate(session, get_employed_crew.user_id, user_email)
#     if isinstance(validation_result, JSONResponse):
#         return validation_result
#     chat = await crud.chat.get_active(session, id=chat_id)
#     cycles = await crud.cycle.get_all_finished_by_chat_id(session, chat_id=chat_id)
#     cycle_with_messages = []
#     for cycle in cycles:
#         messages = await crud.message.get_all_by_cycle_id(session, cycle_id=cycle.id)
#         message_dtos = [
#             MessageSimple(**message.dict())
#             for message in messages
#         ]
#         cycle_with_messages.append(CycleWithMessage(**cycle.dict(), messages=message_dtos))
#     chat_with_all = ChatWithCycleList(**chat.dict(), cycles=cycle_with_messages)
#     return chat_with_all

@router.get("/{employed_crew_id}/chats/{chat_id}/info", description="채팅방 하위의 모든 정보")
async def read_chat_info(chat_id: Annotated[int, Path(title="The ID of the Chat to get")],
                    employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                    session: SessionDep,
                    user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> ChatWithCycleList | None:
    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    chat = await crud.chat.get_active(session, id=chat_id)
    if get_employed_crew.is_owner:
        cycles = await crud.cycle.get_all_by_chat_id(session, chat_id=chat_id)
        is_owner = True
    else:
        cycles = await crud.cycle.get_all_finished_and_started_by_chat_id(session, chat_id=chat_id)
        is_owner = False
    cycle_with_messages = []
    for cycle in cycles:
        messages = await crud.message.get_all_by_cycle_id(session, cycle_id=cycle.id)
        message_dtos = [
            MessageSimple(**message.dict())
            for message in messages
        ]
        cycle_with_messages.append(CycleWithMessage(**cycle.dict(), messages=message_dtos))
    chat_with_all = ChatWithCycleList(**chat.dict(), cycles=cycle_with_messages, is_owner=is_owner)
    return chat_with_all

@router.delete("/{employed_crew_id}/chats/{chat_id}")
async def delete_chat(chat_id: Annotated[int, Path(title="The ID of the Chat to get")],
                      employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                      session: SessionDep,
                      user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> Chat:
    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    return await crud.chat.soft_delete(session, id=chat_id)

@router.get("/{employed_crew_id}/chats/{chat_id}/cycles")
async def read_cycles(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                               chat_id: Annotated[int, Path(title="The ID of the Chat to get")],
                               session: SessionDep,
                               user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> JSONResponse:
    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    if get_employed_crew.is_owner:
        cycles = await crud.cycle.get_all_by_chat_id(session, chat_id=chat_id)
        is_owner = True
    else:
        cycles = await crud.cycle.get_all_finished_and_started_by_chat_id(session, chat_id=chat_id)
        is_owner = False
    cycle_with_messages = []
    for cycle in cycles:
        messages = await crud.message.get_all_by_cycle_id(session, cycle_id=cycle.id)
        message_dtos = [
            MessageSimple(**message.dict())
            for message in messages
        ]
        cycle_with_messages.append((CycleWithMessage(**cycle.dict(), messages=message_dtos)).dict())
    response_data = {
        "cycles": cycle_with_messages,
        "is_owned": is_owner
    }
    return JSONResponse(content=response_data)

@router.get("/{employed_crew_id}/chats/{chat_id}/cycles/{cycle_id}")
async def read_cycle_by_id(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                           chat_id: Annotated[int, Path(title="The ID of the Chat to get")],
                           cycle_id: Annotated[int, Path(title="The ID of the Cycle to get")], session: SessionDep,
                           user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> CycleWithMessage:
    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    cycle = await crud.cycle.get(session, id=cycle_id)
    messages = await crud.message.get_all_by_cycle_id(session, cycle_id=cycle.id)
    message_dtos = [
        MessageSimple(**message.dict()) for message in messages
    ]
    return CycleWithMessage(**cycle.dict(), messages=message_dtos)


@router.post("/{employed_crew_id}/chats/{chat_id}/messages")
async def create_message(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                         chat_id: Annotated[int, Path(title="The ID of the Chat to get")],
                         message_in: MessageRequest, session: SessionDep,
                         user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> MessageSimple:
    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    cycle = await crud.cycle.create(session, obj_in=CycleCreate(chat_id=chat_id))
    message = await crud.message.create(session,obj_in=MessageCreate(cycle_id=cycle.id, **message_in.dict(), chat_id=chat_id))

    return MessageSimple(**message.dict())



@router.get("/{employed_crew_id}/chats/{chat_id}/messages")
async def read_messages(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                        chat_id: Annotated[int, Path(title="The ID of the Chat to get")], session: SessionDep,user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> list[Message]:
    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    return await crud.message.get_all_by_chat_id(session, chat_id=chat_id)

@router.post("/{employed_crew_id}/chats/{chat_id}/kick-off")
async def kick_off_crew(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                    chat_id: Annotated[int, Path(title="The ID of the Chat to get")],
                     session: SessionDep,
                        user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> Response:
    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    new_cycle = await crud.cycle.create(session, obj_in=CycleCreate(chat_id=chat_id))
    result = await crewAiService.CrewAiStartService(session).start(employed_crew_id=employed_crew_id, chat_id=chat_id, cycle_id=new_cycle.id)
    # await crud.cycle.update_status(session, cycle_id=new_cycle.id, status=CycleStatus.FINISHED)
    # return Response(content="Success")
    return result

@router.post("/{employed_crew_id}/chats/{chat_id}/stop")
async def stop_crew(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")],
                    chat_id: Annotated[int, Path(title="The ID of the Chat to get")],
                    session: SessionDep,
                    user_email: str = Depends(GoogleAuthUtils.get_current_user_email)) -> JSONResponse:
    get_employed_crew = await crud.employed_crew.get_active(session, id=employed_crew_id)
    validation_result = await validate(session, get_employed_crew.user_id, user_email)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    cycle = await crud.cycle.get_latest_by_chat_id(session, chat_id=chat_id)
    logging.info(f"Stopping cycle: {cycle.id}")
    if cycle.status == CycleStatus.FINISHED:
        return Response(content="Cycle already finished")
    result = await crewAiService.CrewAiStartService(session).stop(cycle_id=cycle.id)
    return JSONResponse(content=result)
