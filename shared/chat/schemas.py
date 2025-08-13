import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from shared.chat.models import ChatType
from shared.users.schemas import UserS


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
