from fastapi import WebSocket
from typing import Dict, List
from uuid import UUID


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, List[WebSocket]] = {}
        self.chat_subscriptions: Dict[str, List[int]] = {}

    async def connect(self, user_id: UUID, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: UUID):
        self.active_connections.pop(user_id, None)
        for chat_id in self.chat_subscriptions:
            if user_id in self.chat_subscriptions[chat_id]:
                self.chat_subscriptions[chat_id].remove(user_id)

    def subscribe_to_chat(self, user_id: UUID, chat_id: str):
        if chat_id not in self.chat_subscriptions:
            self.chat_subscriptions[chat_id] = []
        if user_id not in self.chat_subscriptions[chat_id]:
            self.chat_subscriptions[chat_id].append(user_id)

    async def send_message_to_chat(self, chat_id: str, message: str):
        print("Sending message to chat:", chat_id, "Message:", message)
        print(chat_id in self.chat_subscriptions)
        if chat_id in self.chat_subscriptions:
            for user_id in self.chat_subscriptions[chat_id]:
                if user_id in self.active_connections:
                    websockets = self.active_connections[user_id]
                    for websocket in websockets:
                        await websocket.send_text(message)


manager = ConnectionManager()
