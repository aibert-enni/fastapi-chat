from typing import Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError as SQLIntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from shared.core.utils import hash_password
from shared.error.custom_exceptions import IntegrityError, NotFoundError
from shared.users.models import User
from shared.users.schemas import SuperUserCreateS, SuperUserUpdateS, UserCreateS


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
        except SQLIntegrityError as e:
            detail = str(e.orig)
            if "username" in detail:
                raise IntegrityError(
                    "User with this username already exist",
                )
            elif "email" in detail:
                raise IntegrityError(
                    "User with this email already exist",
                )
            else:
                raise IntegrityError("Unique constraint violation")
        await session.refresh(db_user)

        return db_user

    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str) -> User:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise NotFoundError(message="User not found")
        return db_user

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise NotFoundError(message="User not found")
        return db_user

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> User:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise NotFoundError(message="User not found")
        return db_user

    @classmethod
    async def delete_user(cls, session: AsyncSession, user: User) -> None:
        await session.delete(user)
        await session.commit()

    @staticmethod
    async def update_user(
        session: AsyncSession, db_user: User, user_data: SuperUserUpdateS
    ) -> User:
        for key, value in user_data.model_dump().items():
            setattr(db_user, key, value)

        await session.commit()
        await session.refresh(db_user)
        return db_user

    @staticmethod
    async def activate_user(session: AsyncSession, user: User) -> User:
        if user.is_active:
            return User
        user.is_active = True
        await session.commit()
        await session.refresh(user)
        return user
