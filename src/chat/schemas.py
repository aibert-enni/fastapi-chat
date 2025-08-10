import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from chat.models import ChatType
from users.schemas import UserS


class ChatS(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    type: ChatType
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class ChatCreateS(BaseModel):
    name: str
    description: Optional[str] = None


class MessageCreateS(BaseModel):
    content: str


class ChatUserS(UserS):
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)


class MessageInfoS(BaseModel):
    id: UUID
    user_id: UUID
    username: str
    created_at: datetime.datetime
    content: str

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class WSMessageBase(BaseModel):
    action: str


class WSSubscribe(WSMessageBase):
    action: str = "subscribe"
    chat_ids: List[str] = Field(..., min_items=1)


class WSMessage(WSMessageBase):
    action: str = "message"
    chat_id: str
    text: str = Field(..., min_length=1, max_length=1000)
