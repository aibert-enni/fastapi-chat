from typing import Tuple, Union

from sqlalchemy.ext.asyncio import AsyncSession

from shared.auth.models import EmailVerification
from shared.auth.schemas import UserAuthenticateS
from shared.auth.utils import (
    TOKEN_TYPE_FIELD,
    TokenType,
    generate_verification_token,
)
from shared.core.utils import hash_password, verify_password
from shared.error.custom_exceptions import (
    CredentialError,
    ValidationError,
)
from shared.users.models import User
from shared.users.schemas import UserBaseS
from shared.users.services import UserService


class AuthService:
    @staticmethod
    async def authenticate_user(session: AsyncSession, user: UserAuthenticateS) -> User:
        db_user = await UserService.get_user_by_username(session, user.username)
        if not verify_password(user.password, db_user.password):
            raise CredentialError(message="Username or Password incorrect")
        return user

    @classmethod
    async def get_user_by_token(
        cls,
        session: AsyncSession,
        payload: dict,
        token_type: TokenType = TokenType.ACCESS,
    ) -> Union[User, None]:
        if payload.get(TOKEN_TYPE_FIELD) != token_type.value:
            raise CredentialError

        username = payload.get("sub")
        if username is None:
            raise CredentialError

        token_data = UserBaseS(username=username)

        user = await UserService.get_user_by_username(session, token_data.username)

        return user

    async def change_user_password(
        session: AsyncSession, user: User, current_password: str, new_password: str
    ) -> User:
        if current_password == new_password:
            raise ValidationError(
                message="The new password and the current password must be different"
            )

        if not verify_password(current_password, user.password):
            raise ValidationError(message="The current password does not match")

        new_hashed_password = hash_password(new_password)
        user.password = new_hashed_password

        await session.commit()
        await session.refresh(user)

        return User

    @staticmethod
    async def create_email_verification(
        session: AsyncSession, user: User
    ) -> Tuple[EmailVerification, str]:
        raw_token, hash_token = generate_verification_token()
        email = EmailVerification(user_id=user.id, token_hash=hash_token)
        session.add(email)
        await session.commit()
        await session.refresh(email)
        return email, raw_token
