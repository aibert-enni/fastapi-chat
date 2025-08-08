import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from users.schemas import UserS


class ChatCreateS(BaseModel):
    name: str
    description: Optional[str] = None


class MessageCreateS(BaseModel):
    content: str


class ChatUserS(UserS):
    is_admin: bool = False

    class Config:
        from_attributes = True


class MessageInfoS(BaseModel):
    id: UUID
    user_id: UUID
    username: str
    created_at: datetime
    content: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
