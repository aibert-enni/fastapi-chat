from typing import Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from users.schemas import SuperUserCreateS, SuperUserUpdateS, UserCreateS
from core.utils import hash_password
from users.models import User


class UserService:
    @staticmethod
    async def create_user(
        session: AsyncSession, user: Union[UserCreateS, SuperUserCreateS]
    ) -> User:
        hashed = hash_password(user.password)
        user.password = hashed
        db_user = User(**user.model_dump())

        session.add(db_user)

        try:
            await session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким username уже существует",
            )
        await session.refresh(db_user)

        return db_user

    @staticmethod
    async def get_user_by_username(
        session: AsyncSession, username: str
    ) -> Union[User, None]:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return db_user

    @classmethod
    async def delete_user(cls, session: AsyncSession, user: User) -> None:
        await session.delete(user)
        await session.commit()

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return db_user

    @staticmethod
    async def update_user(
        session: AsyncSession, db_user: User, user_data: SuperUserUpdateS
    ) -> User:
        for key, value in user_data.model_dump().items():
            setattr(db_user, key, value)

        await session.commit()
        await session.refresh(db_user)
        return db_user
