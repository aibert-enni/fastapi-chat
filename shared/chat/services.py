from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.users.models import User
from shared.chat.models import Chat, ChatType, ChatUser, Message
from shared.chat.schemas import ChatCreateS, ChatUserS, MessageInfoS


class ChatService:

    @staticmethod
    async def create_chat(
        session: AsyncSession, chat: ChatCreateS, type: ChatType
    ) -> Chat:
        db_chat = Chat(**chat.model_dump(), type=type)
        session.add(db_chat)
        await session.commit()
        await session.refresh(db_chat)
        return db_chat

    @staticmethod
    async def get_private_chat(session: AsyncSession, user_one: User, user_two: User):
        subq = (
            select(ChatUser.chat_id)
            .group_by(ChatUser.chat_id)
            .having(func.count(ChatUser.user_id) == 2)
            .having(func.bool_and(ChatUser.user_id.in_([user_one.id, user_two.id])))
            .subquery()
        )
        query = select(Chat).where(
            and_(
                Chat.id.in_(select(subq.c.chat_id)),
                Chat.type == ChatType.PRIVATE,
            )
        )
        result = await session.execute(query)
        chat = result.scalars().first()

        return chat

    @classmethod
    async def create_private_chat(
        cls, session: AsyncSession, user_one: User, user_two: User
    ) -> Chat:
        exist_chat = await cls.get_private_chat(session, user_one, user_two)
        if exist_chat:
            raise HTTPException(
                detail={"error": "Chat already exist"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        db_chat = await cls.create_chat(
            session,
            ChatCreateS(name=f"{user_one.username} & {user_two.username}"),
            ChatType.PRIVATE,
        )
        await cls.add_user_to_chat(session, db_chat, user_one)
        await cls.add_user_to_chat(session, db_chat, user_two)
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
    async def get_user_chat_ids_in_list(
        session: AsyncSession, user: User, chat_ids: list[str]
    ) -> list[UUID]:
        stmt = select(ChatUser.chat_id).where(
            ChatUser.user_id == user.id, Chat.id.in_(chat_ids)
        )
        result = await session.execute(stmt)
        chat_ids = result.scalars().all()
        return chat_ids

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
    async def get_user_chats(session: AsyncSession, user_id: int) -> list[Chat]:
        stmt = select(Chat).where(User.id == user_id)
        result = await session.execute(stmt)
        chats = result.scalars().all()
        return chats

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
