from typing import List, Optional
from pydantic import BaseModel, Field


class WSMessageBase(BaseModel):
    action: str
    user_id: Optional[str] = None


class WSSubscribe(WSMessageBase):
    action: str = "subscribe"
    chat_ids: List[str] = Field(..., min_items=1)


class WSMessage(WSMessageBase):
    action: str = "message"
    chat_id: str
    text: str = Field(..., min_length=1, max_length=1000)
