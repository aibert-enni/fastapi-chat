from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError as SAIntegrityError

from ddd_shared.application.mappers.user import UserMapper
from ddd_shared.infra.domain.repositories.exceptions import IntegrityError
from ddd_shared.infra.domain.repositories.user_repository import IUserRepository
from shared.users.models import User as UserDB

from .base import BaseSQLAlchemyRepository


class UserRepository(BaseSQLAlchemyRepository, IUserRepository):
    async def save(self, user):
        db_user = UserMapper.to_db(user)
        self.session.add(db_user)
        try:
            await self.session.flush()
            await self.session.refresh(db_user)
        except SAIntegrityError as e:
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
        return UserMapper.to_domain(db_user)

    async def get_user_by_id(self, user_id: UUID):
        stmt = select(UserDB).where(UserDB.id == user_id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()

        if db_user:
            return UserMapper.to_domain(db_user)
        return None

    async def get_user_by_username(self, username: str):
        stmt = select(UserDB).where(UserDB.username == username)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user:
            return UserMapper.to_domain(db_user)
        return None

    async def get_user_by_email(self, email: str):
        stmt = select(UserDB).where(UserDB.email == email)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user:
            return UserMapper.to_domain(db_user)
        return None
