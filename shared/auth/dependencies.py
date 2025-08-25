from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from shared.auth.services import AuthService
from shared.auth.utils import TokenType, decode_jwt
from shared.database import SessionDep
from shared.error.custom_exceptions import AuthorizationError, CredentialError
from shared.users.models import User

http_bearer = HTTPBearer(auto_error=False)


def get_current_token_payload(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> dict:
    """
    Retrieve the payload from the JWT token provided in the HTTP authorization credentials.
    """
    if credential is None:
        raise CredentialError
    try:
        token = credential.credentials
        payload = decode_jwt(token)
    except Exception:
        raise CredentialError
    return payload


async def get_current_user(
    session: SessionDep,
    payload: dict = Depends(get_current_token_payload),
) -> User:
    """
    Retrieve the current user based on the provided HTTP authorization credentials.
    """
    try:
        user = await AuthService.get_user_by_token(session, payload)
    except Exception:
        raise CredentialError

    if user is None:
        raise CredentialError

    if not user.is_active:
        raise CredentialError(message="Account not activated")

    return user


async def get_current_user_by_refresh(session: SessionDep, request: Request) -> User:
    """
    Retrieve the current user based on the refresh token stored in cookies.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise CredentialError
    try:
        payload = decode_jwt(refresh_token)
    except Exception:
        raise CredentialError

    user = await AuthService.get_user_by_token(
        session, payload, token_type=TokenType.REFRESH
    )

    if user is None:
        raise CredentialError

    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the current user is a superuser.
    """
    if not current_user.is_superuser:
        raise AuthorizationError
    return current_user


GetCurrentUserDep = Annotated[User, Depends(get_current_user)]
GetCurrentUserByRefreshDep = Annotated[User, Depends(get_current_user_by_refresh)]

GetCurrentSuperUserDep = Annotated[User, Depends(get_current_superuser)]
