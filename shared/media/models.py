from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlalchemy import UUID, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from shared.core.models import BaseUUID


class Image(BaseUUID):
    __tablename__ = "images"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    owner_type: Mapped[str] = mapped_column(nullable=False)
    file_path: Mapped[str] = mapped_column(nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    alt_text: Mapped[Optional[str]] = mapped_column(nullable=True)

    owner: Mapped["User"] = relationship("User", back_populates="images")
