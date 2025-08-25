from datetime import datetime, timedelta, timezone
from typing import Tuple, Union

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.auth.models import EmailVerification
from shared.auth.schemas import UserAuthenticateS
from shared.auth.tasks import send_email
from shared.auth.utils import (
    TOKEN_TYPE_FIELD,
    TokenType,
    generate_verification_token,
    hash_token,
)
from shared.core.utils import hash_password, verify_password
from shared.error.custom_exceptions import (
    APIError,
    CredentialError,
    NotFoundError,
    ValidationError,
)
from shared.settings import settings
from shared.users.models import User
from shared.users.schemas import UserBaseS
from shared.users.services import UserService


class AuthService:
    @staticmethod
    async def authenticate_user(session: AsyncSession, user: UserAuthenticateS) -> User:
        db_user = await UserService.get_user_by_username(session, user.username)
        if not verify_password(user.password, db_user.password):
            raise CredentialError(message="Username or Password incorrect")
        if not db_user.is_active:
            raise CredentialError(message="Account not activated")
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

    @staticmethod
    async def activate_email_verification(
        session: AsyncSession, email_verification: EmailVerification
    ) -> EmailVerification:
        if email_verification.is_used:
            return email_verification
        email_verification.is_used = True
        await session.commit()
        await session.refresh(email_verification)
        return email_verification

    @staticmethod
    async def get_email_verification_by_token(
        session: AsyncSession, token: str
    ) -> EmailVerification:
        hashed_token = hash_token(token)
        stmt = (
            select(EmailVerification)
            .options(selectinload(EmailVerification.user))
            .where(EmailVerification.token_hash == hashed_token)
        )
        result = await session.execute(stmt)

        email = result.scalar_one_or_none()

        if email is None:
            raise NotFoundError(message="Token invalid")

        return email

    @staticmethod
    async def get_last_user_email_verification_or_none(
        session: AsyncSession, user: User
    ) -> Union[EmailVerification, None]:
        stmt = select(EmailVerification).where(EmailVerification.user_id == user.id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def send_email_verification(
        cls, session: AsyncSession, user: User
    ) -> Tuple[EmailVerification, str]:
        email_verification = await cls.get_last_user_email_verification_or_none(
            session, user
        )
        if email_verification is None:
            email_verification, raw = await AuthService.create_email_verification(
                session, user
            )
        else:
            diff_minutes = (
                datetime.now(timezone.utc) - email_verification.sent_at
            ).total_seconds() / 60
            if diff_minutes < settings.email.SEND_LIMIT_MINUTES:
                try_after = int(settings.email.SEND_LIMIT_MINUTES - diff_minutes)
                raise APIError(
                    message=f"You already sent email, try after {try_after} minutes",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error="Bad Request Error",
                )

            raw, hashed = generate_verification_token()
            email_verification.token_hash = hashed
            email_verification.expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.email.EXPIRE_MINUTES
            )
            await session.commit()
            await session.refresh(email_verification)
        send_email.delay(to=user.email, subject="Email verification", body=raw)
        return email_verification, raw
