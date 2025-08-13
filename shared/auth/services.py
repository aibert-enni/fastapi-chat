from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import status

from shared.users.models import User
from shared.auth.schemas import UserAuthenticateS
from shared.users.schemas import UserBaseS
from shared.auth.utils import (
    TOKEN_TYPE_FIELD,
    TokenType,
    credentials_exception,
)
from shared.core.utils import hash_password, verify_password
from shared.users.services import UserService


class AuthService:

    @staticmethod
    async def authenticate_user(session: AsyncSession, user: UserAuthenticateS) -> User:
        db_user = await UserService.get_user_by_username(session, user.username)
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

        token_data = UserBaseS(username=username)

        user = await UserService.get_user_by_username(session, token_data.username)

        return user

    async def change_user_password(
        session: AsyncSession, user: User, current_password: str, new_password: str
    ) -> User:
        if not verify_password(current_password, user.password):
            raise HTTPException(detail={"error": "Password does not match"})

        new_hashed_password = hash_password(new_password)
        user.password = new_hashed_password

        await session.commit()
        await session.refresh(user)

        return User
