import asyncio
import logging
from fastapi import WebSocket
from typing import Dict, Set
from uuid import UUID

from fastapi.websockets import WebSocketState

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
        self.chat_subscriptions: Dict[UUID, Set[UUID]] = {}

    async def connect(self, user_id: UUID, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(
            f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}"
        )

    def disconnect(self, ws: WebSocket, user_id: UUID):
        if user_id not in self.active_connections:
            return

        connections = self.active_connections[user_id]

        if ws in connections:
            connections.remove(ws)
            logger.info(
                f"WebSocket disconnected for user {user_id}. Remaining connections: {len(connections)}"
            )

        if not connections:
            self.active_connections.pop(user_id, None)
            for chat_id in list(self.chat_subscriptions.keys()):
                if user_id in self.chat_subscriptions[chat_id]:
                    self.chat_subscriptions[chat_id].remove(user_id)
                    logger.info(f"User {user_id} unsubscribed from chat {chat_id}")
                if not self.chat_subscriptions[chat_id]:
                    self.chat_subscriptions.pop(chat_id)
                    logger.info(
                        f"No subscribers left for chat {chat_id}. Chat removed."
                    )

    def subscribe_to_chat(self, user_id: UUID, chat_id: UUID):
        if chat_id not in self.chat_subscriptions:
            self.chat_subscriptions[chat_id] = set()
        self.chat_subscriptions[chat_id].add(user_id)
        logger.info(f"User {user_id} subscribed to chat {chat_id}")

    async def send_json_to_user(self, user_id: UUID, data: dict):
        if user_id not in self.active_connections:
            logger.warning(f"Tried to send data to disconnected user {user_id}")
            return
        websockets = self.active_connections[user_id]
        await asyncio.gather(*(self._safe_send_json(ws, data) for ws in websockets))

    async def _safe_send_json(self, ws: WebSocket, data: dict):
        try:
            if ws.client_state == WebSocketState.CONNECTED:
                await ws.send_json(data)
        except Exception as e:
            logger.error(f"Error sending JSON: {e}")

    async def send_json_to_chat(self, chat_id: UUID, data: dict) -> bool:
        if chat_id not in self.chat_subscriptions:
            logger.warning(f"Chat {chat_id} has no subscribers")
            return False

        for user_id in self.chat_subscriptions[chat_id]:
            await self.send_json_to_user(user_id, data)

        return True


manager = ConnectionManager()
