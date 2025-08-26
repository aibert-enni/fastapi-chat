from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from ddd_shared.infra.domain.enteties.user import User


@dataclass
class EmailVerification:
    user_id: UUID
    token_hash: str
    expires_at: datetime
    sent_at: datetime
    is_used: bool
    id: Optional[UUID] = None
    user: Optional[User] = None
