from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.core.models import BaseUUID

if TYPE_CHECKING:
    from shared.auth.models import EmailVerification
    from shared.chat.models import Chat, ChatUser, Message
    from shared.media.models import Image


class User(BaseUUID):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    fullname: Mapped[Optional[str]]

    password: Mapped[str] = mapped_column(String(128))

    is_active: Mapped[bool] = mapped_column(default=False, server_default="false")

    is_superuser: Mapped[bool] = mapped_column(default=False, server_default="false")

    chats: Mapped[list["ChatUser"]] = relationship(
        "ChatUser",
        back_populates="user",
        cascade="all, delete-orphan",
        overlaps="chats",
    )

    chat_participations: Mapped[list["Chat"]] = relationship(
        "Chat",
        secondary="chat_users",
        back_populates="user_participants",
        overlaps="chats,users",
    )

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="user")

    images: Mapped[list["Image"]] = relationship("Image", back_populates="owner")

    email_verifications: Mapped[list["EmailVerification"]] = relationship(
        "EmailVerification", back_populates="user"
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, name={self.username!r}, fullname={self.fullname!r})"
        )
