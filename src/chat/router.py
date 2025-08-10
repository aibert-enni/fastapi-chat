from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.params import Query
from fastapi.websockets import WebSocketState
from pydantic import ValidationError

from chat.models import ChatType
from chat.schemas import ChatCreateS, ChatS, WSMessage, WSSubscribe
from chat.services import ChatService
from chat.utils import parse_ws_message
from chat.websocket_handlers import handle_message, handle_subscribe
from database import SessionDep
from auth.dependencies import GetCurrentUserDep, get_current_user
from users.models import User
from chat.manager import manager
from auth.utils import decode_jwt, credentials_exception
from auth.services import AuthService
from users.services import UserService

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
            try:
                data = await websocket.receive_json()
                message = parse_ws_message(data)
                if isinstance(message, WSMessage):
                    await handle_message(user, session, message.model_dump(), manager)
                elif isinstance(message, WSSubscribe):
                    await handle_subscribe(user, session, message.model_dump(), manager)
            except ValidationError as e:
                await websocket.send_json({"error": str(e), "status": "error"})
            except ValueError as e:
                await websocket.send_json({"error": str(e), "status": "error"})
    except Exception as e:
        print(f"Disconnected: {e}")
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close(code=1001)
            except WebSocketDisconnect:
                pass
        manager.disconnect(websocket, user.id)


@router.get("/{chat_id}")
async def get_chat(chat_id: UUID, session: SessionDep):
    db_chat = await ChatService.get_chat(session, chat_id)
    return {"chat": db_chat}


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
