from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import UUID, UniqueConstraint

from core.models import BaseUUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey


class Chat(BaseUUID):
    __tablename__ = "chats"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )

    users: Mapped[list["ChatUser"]] = relationship(
        "ChatUser",
        back_populates="chat",
        cascade="all, delete-orphan",
        overlaps="chat_participations",
    )

    user_participants: Mapped[list["User"]] = relationship(
        "User",
        secondary="chat_users",
        back_populates="chat_participations",
        overlaps="chats,users",
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="chat",
    )

    def __repr__(self):
        return f"<Chat id={self.id} name={self.name} description={self.description}>"


class Message(BaseUUID):
    __tablename__ = "messages"

    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    user: Mapped["User"] = relationship("User", back_populates="messages")

    def __repr__(self):
        return f"<Message id={self.id} chat_id={self.chat_id} user_id={self.user_id} content={self.content}>"


class ChatUser(BaseUUID):
    __tablename__ = "chat_users"

    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)

    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    chat: Mapped["Chat"] = relationship(
        "Chat", back_populates="users", overlaps="chat_participations,user_participants"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="chats", overlaps="chat_participations,user_participants"
    )

    __table_args__ = (UniqueConstraint("chat_id", "user_id", name="uq_chat_user"),)

    def __repr__(self):
        return f"<ChatUser id={self.id} chat_id={self.chat_id} user_id={self.user_id}>"
