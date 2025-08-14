import json
import logging
from typing import Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from shared.websocket.schemas import WSMessage, WSPushNotificationS, WSSubscribe
from app_ws.utils import parse_ws_message
from shared.chat.services import ChatService
from shared.database import session_context
from shared.users.services import UserService

from .ws_manager import ConnectionManager, manager
from shared.users.models import User

logger = logging.getLogger(__name__)


class ChatWSService:
    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    async def _handle_subscribe(
        self, user: User, session: AsyncSession, data: WSSubscribe
    ):
        chat_ids = data.chat_ids
        chat_ids_to_subscribe = await ChatService.get_user_chat_ids_in_list(
            session, user, chat_ids
        )
        for chat_id in chat_ids_to_subscribe:
            self.manager.subscribe_to_chat(user.id, chat_id)

        results = []
        for id in chat_ids:
            if id in chat_ids_to_subscribe:
                results.append({"chat_id": str(id), "status": "success"})
            else:
                results.append(
                    {"chat_id": str(id), "status": "error", "error": "no access"}
                )

        await self.manager.send_json_to_user(
            user.id, {"action": "subscribe_response", "results": results}
        )

    async def _handle_message(self, user: User, session: AsyncSession, data: WSMessage):
        is_sent = await self.manager.send_json_to_chat(
            data.chat_id,
            {
                "from": user.username,
                "message": f"{data.text}",
                "chat_id": str(data.chat_id),
            },
        )
        response = {"action": "message_response"}
        if is_sent:
            await ChatService.create_message(session, data.chat_id, user.id, data.text)
            response["status"] = "success"
        else:
            response["status"] = "error"
            response["error"] = "Couldn't send message"
        await self.manager.send_json_to_user(user.id, response)

    async def _handle_push_notification(self, user: User, data: WSPushNotificationS):
        await self.manager.send_json_to_user(
            user.id,
            data.model_dump(mode="json"),
        )

    @staticmethod
    def safe_parse_message(payload: dict):
        try:
            action = payload.get("action")
            if action == "push_notification":
                return WSPushNotificationS(**payload)
            else:
                return parse_ws_message(payload)
        except ValueError as e:
            logger.error(f"Invalid WS message format: {e}")
            return None

    async def handle_data(self, data: str):
        try:
            payload = json.loads(data)
        except TypeError as e:
            logger.error(f"Invalid JSON message: {e}")
            return
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message: {e}")
            return

        ws_message = self.safe_parse_message(payload)

        if not ws_message:
            return

        try:
            async with session_context() as session:
                user = await UserService.get_user_by_id(session, ws_message.user_id)
                if not user:
                    logger.warning(f"User {ws_message.user_id} not found")
                    return

                if isinstance(ws_message, WSMessage):
                    await self._handle_message(
                        user,
                        session,
                        ws_message,
                    )
                elif isinstance(ws_message, WSSubscribe):
                    await self._handle_subscribe(
                        user,
                        session,
                        ws_message,
                    )
                elif isinstance(ws_message, WSPushNotificationS):
                    await self._handle_push_notification(user, ws_message)
                else:
                    raise ValueError(f"Unknown WS message type: {type(ws_message)}")
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            try:
                await self.manager.send_json_to_user(
                    UUID(ws_message.user_id),
                    {
                        "status": "error",
                        "error": "Message processing failed",
                    },
                )
            except Exception as send_err:
                logger.error(f"Failed to send error message to user: {send_err}")


chat_ws_service = ChatWSService(manager)
