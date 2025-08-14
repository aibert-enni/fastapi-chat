from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class WSMessageBase(BaseModel):
    action: str
    user_id: Optional[UUID] = None


class WSSubscribe(WSMessageBase):
    action: str = "subscribe"
    chat_ids: List[UUID] = Field(..., min_items=1)


class WSMessage(WSMessageBase):
    action: str = "message"
    chat_id: UUID
    text: str = Field(..., min_length=1, max_length=1000)


class WSPushNotificationS(WSMessageBase):
    message: str
