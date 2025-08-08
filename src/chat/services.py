from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from chat.models import Chat, ChatUser, Message
from chat.schemas import ChatCreateS, ChatUserS, MessageInfoS


class ChatService:

    @staticmethod
    async def create_chat(session: AsyncSession, chat: ChatCreateS) -> Chat:
        db_chat = Chat(**chat.model_dump())
        session.add(db_chat)
        await session.commit()
        await session.refresh(db_chat)
        return db_chat

    @staticmethod
    async def get_chat(session: AsyncSession, chat_id: UUID) -> Chat:
        stmt = select(Chat).where(Chat.id == chat_id)
        result = await session.execute(stmt)
        db_chat = result.scalar_one_or_none()
        if db_chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        return db_chat

    @staticmethod
    async def add_user_to_chat(
        session: AsyncSession, chat: Chat, user: User, is_admin: bool = False
    ) -> None:
        chat_user = ChatUser(chat_id=chat.id, user_id=user.id, is_admin=is_admin)
        session.add(chat_user)
        await session.commit()

    @staticmethod
    async def get_chat_users(session: AsyncSession, chat: Chat) -> list[ChatUserS]:
        stmt = (
            select(User, ChatUser.is_admin)
            .join(ChatUser)
            .where(ChatUser.chat_id == chat.id)
        )
        result = await session.execute(stmt)
        users = result.scalars().all()
        users_schemas = [ChatUserS.model_validate(user) for user in users]
        return users_schemas

    @staticmethod
    async def create_message(
        session: AsyncSession, chat_id: UUID, user_id: UUID, message: str
    ) -> Message:
        db_message = Message(chat_id=chat_id, user_id=user_id, content=message)
        session.add(db_message)
        await session.commit()
        await session.refresh(db_message)
        return db_message

    @staticmethod
    async def get_messages_by_chat(
        session: AsyncSession, chat_id: UUID
    ) -> list[MessageInfoS]:
        stmt = (
            select(Message, User.username).join(User).where(Message.chat_id == chat_id)
        )
        result = await session.execute(stmt)
        messages = result.all()
        messages_schemas = [
            MessageInfoS(
                id=m.id,
                user_id=m.user_id,
                username=username,  # <- вручную
                created_at=m.created_at,
                content=m.content,
            )
            for m, username in messages
        ]
        return messages_schemas
