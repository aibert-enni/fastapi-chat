from typing import Union
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import status

from auth.models import User
from auth.schemas import UserAuthenticateS, UserCreateS, UserS
from auth.utils import (
    TOKEN_TYPE_FIELD,
    TokenType,
    decode_jwt,
    credentials_exception,
)
from core.utils import hash_password, verify_password


class AuthService:

    @staticmethod
    async def create_user(session: AsyncSession, user: UserCreateS) -> User:
        hashed = hash_password(user.password)
        user.password = hashed
        db_user = User(**user.model_dump())

        session.add(db_user)

        await session.commit()
        await session.refresh(db_user)

        return db_user

    @staticmethod
    async def get_user(session: AsyncSession, username: str) -> Union[User, None]:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()
        return db_user

    @classmethod
    async def authenticate_user(
        cls, session: AsyncSession, user: UserAuthenticateS
    ) -> User:
        db_user = await cls.get_user(session, user.username)
        if db_user == None:
            raise HTTPException(
                status_code=400, detail="username или пароль неправильный"
            )
        if not verify_password(user.password, db_user.password):
            raise HTTPException(
                status_code=400, detail="username или пароль неправильный"
            )
        return user

    @classmethod
    async def get_user_by_token(
        cls,
        session: AsyncSession,
        payload: dict,
        token_type: TokenType = TokenType.ACCESS,
    ) -> Union[User, None]:
        if payload.get(TOKEN_TYPE_FIELD) != token_type.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        if username is None:
            raise credentials_exception

        token_data = UserS(username=username)

        user = await cls.get_user(session, token_data.username)

        return user
