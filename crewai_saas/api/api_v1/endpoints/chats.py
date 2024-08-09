from fastapi import APIRouter, Path
from typing import Annotated

from crewai_saas.api.deps import CurrentUser, SessionDep
from crewai_saas.crud import chat
from crewai_saas.model import Chat, ChatCreate

router = APIRouter()

@router.post("/")
async def create_chat(chat_in: ChatCreate, session: SessionDep) -> Chat:
    return await chat.create(session, obj_in=chat_in)

@router.get("/")
async def read_chats(employed_crew_id: Annotated[int, Path(title="The ID of the Employed Crew to get")], session: SessionDep) -> list[Chat]:
    return await chat.get_all_active_by_employed_crew_id(session, employed_crew_id=employed_crew_id)


@router.get("/{chat_id}")
async def read_chat(chat_id: Annotated[int, Path(title="The ID of the Chat to get")],
                    session: SessionDep) -> Chat | None:
    return await chat.get_active(session, id=chat_id)

@router.delete("/{chat_id}")
async def delete_chat(chat_id: Annotated[int, Path(title="The ID of the Chat to get")],
                      session: SessionDep) -> Chat:
    return await chat.soft_delete(session, id=chat_id)