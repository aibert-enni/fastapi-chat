import logging
from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from shared.chat.models import ChatType
from shared.chat.schemas import ChatCreateS, ChatS
from shared.chat.services import ChatService
from shared.database import SessionDep
from shared.auth.dependencies import GetCurrentUserDep, get_current_user
from shared.users.models import User
from shared.users.services import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/{chat_id}")
async def get_chat(chat_id: UUID, session: SessionDep):
    db_chat = await ChatService.get_chat(session, chat_id)
    return {"chat": db_chat}


@router.delete("/{chat_id}")
async def delete_chat(chat_id: UUID, session: SessionDep):
    await ChatService


@router.post("/group")
async def create_group_chat(
    chat: ChatCreateS, session: SessionDep, user: GetCurrentUserDep
):
    db_chat = await ChatService.create_chat(session, chat, ChatType.GROUP)
    await ChatService.add_user_to_chat(session, db_chat, user, is_admin=True)
    return {"chat": db_chat}


@router.post("/{user_id}")
async def create_private_chat(
    user_id: str, session: SessionDep, current_user: GetCurrentUserDep
) -> ChatS:
    target_user = await UserService.get_user_by_id(session, user_id)
    db_chat = await ChatService.create_private_chat(session, current_user, target_user)
    return db_chat


@router.post("/{chat_id}/users")
async def add_user_to_chat(
    chat_id: UUID,
    session: SessionDep,
    user: User = Depends(get_current_user),
):
    chat = await ChatService.get_chat(session, chat_id)
    if chat.type == ChatType.PRIVATE:
        raise HTTPException(
            detail={"error": "Chat isn't exist"}, status_code=status.HTTP_404_NOT_FOUND
        )
    await ChatService.add_user_to_chat(session, chat_id, user)
    return {"message": "User joined to chat successfully."}


@router.get("/{chat_id}/users")
async def get_chat_users(chat_id: UUID, session: SessionDep):
    chat = await ChatService.get_chat(session, chat_id)
    users = await ChatService.get_chat_users(session, chat)

    return {"users": users}


@router.get("/{chat_id}/messages")
async def get_chat_messages(chat_id: UUID, session: SessionDep):
    messages = await ChatService.get_messages_by_chat(session, chat_id)
    return {"messages": messages}


@router.get("/user_chats/{user_id}")
async def get_user_chats(user_id: UUID, session: SessionDep) -> list[ChatS]:
    chats = await ChatService.get_user_chats(session, user_id)
    return chats
