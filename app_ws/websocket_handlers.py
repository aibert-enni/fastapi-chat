from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from .ws_manager import ConnectionManager
from shared.chat.services import ChatService
from shared.users.models import User


async def handle_subscribe(
    user: User, session: AsyncSession, data: dict, manager: ConnectionManager
):
    chat_ids = data.get("chat_ids", [])
    chat_ids_to_subscribe = await ChatService.get_user_chat_ids_in_list(
        session, user, chat_ids
    )
    for chat_id in chat_ids_to_subscribe:
        manager.subscribe_to_chat(user.id, str(chat_id))

    results = []

    chat_ids = [UUID(str(id)) for id in chat_ids]
    for id in chat_ids:
        if id in chat_ids_to_subscribe:
            results.append({"chat_id": str(id), "status": "success"})
        else:
            results.append(
                {"chat_id": str(id), "status": "error", "error": "no access"}
            )

    await manager.send_json_to_user(
        user.id, {"action": "subscribe_response", "results": results}
    )


async def handle_message(
    user: User, session: AsyncSession, data: dict, manager: ConnectionManager
):
    chat_id = data.get("chat_id")
    text = data.get("text")
    is_sent = await manager.send_json_to_chat(
        chat_id,
        {
            "from": user.username,
            "message": f"{text}",
            "chat_id": chat_id,
        },
    )
    response = {"action": "message_response"}
    if is_sent:
        await ChatService.create_message(session, chat_id, user.id, text)
        response["status"] = "success"
    else:
        response["status"] = "error"
        response["error"] = "Couldn't send message"
    await manager.send_json_to_user(user.id, response)
