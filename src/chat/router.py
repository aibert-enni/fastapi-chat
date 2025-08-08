from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket
from fastapi.params import Query

from users.schemas import UserS
from chat.schemas import ChatCreateS
from chat.services import ChatService
from database import SessionDep
from auth.dependencies import GetCurrentUserDep, get_current_user
from users.models import User
from chat.manager import manager
from auth.utils import decode_jwt, credentials_exception
from auth.services import AuthService

router = APIRouter(prefix="/chats", tags=["chats"])


@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    session: SessionDep,
    token: str = Query(...),
):

    try:
        payload = decode_jwt(token)
    except Exception:
        raise credentials_exception

    user = await AuthService.get_user_by_token(session, payload)

    await manager.connect(user.id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if action == "subscribe":
                chat_ids = data.get("chat_ids", [])
                print(chat_ids)
                for chat_id in chat_ids:
                    manager.subscribe_to_chat(user.id, chat_id)
            if action == "message":
                chat_id = data.get("chat_id")
                text = data.get("text")
                await ChatService.create_message(session, chat_id, user.id, text)
                await manager.send_message_to_chat(chat_id, f"{user.username}: {text}")
    except Exception as e:
        print(f"Disconnected: {e}")
    finally:
        manager.disconnect(user.id)


@router.get("/{chat_id}")
async def get_chat(chat_id: UUID, session: SessionDep):
    db_chat = await ChatService.get_chat(session, chat_id)
    return {"chat": db_chat}


@router.post("/")
async def create_chat(chat: ChatCreateS, session: SessionDep, user: GetCurrentUserDep):
    db_chat = await ChatService.create_chat(session, chat)
    await ChatService.add_user_to_chat(session, db_chat, user, is_admin=True)
    return {"chat": db_chat}


@router.post("/{chat_id}/users")
async def add_user_to_chat(
    chat_id: UUID,
    session: SessionDep,
    user: User = Depends(get_current_user),
):
    await ChatService.add_user_to_chat(session, chat_id, user)
    return {"message": "User joined to chat successfully."}


@router.get("/{chat_id}/users")
async def get_chat_users(chat_id: UUID, session: SessionDep):
    chat = await ChatService.get_chat(session, chat_id)
    users = await ChatService.get_chat_users(session, chat)

    return {"users": users}


@router.get("{chat_id}/messages")
async def get_chat_messages(chat_id: UUID, session: SessionDep):
    messages = await ChatService.get_messages_by_chat(session, chat_id)
    return {"messages": messages}
