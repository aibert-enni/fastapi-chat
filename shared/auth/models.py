from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from sqlalchemy import UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.core.models import BaseUUID
from shared.settings import settings

if TYPE_CHECKING:
    from shared.users.models import User


class EmailVerification(BaseUUID):
    __tablename__ = "email_verifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
        + timedelta(minutes=settings.email.EXPIRE_MINUTES),
        nullable=False,
    )
    is_used: Mapped[bool] = mapped_column(default=False, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="email_verifications")
