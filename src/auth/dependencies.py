from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from auth.models import User
from auth.services import AuthService
from auth.utils import TOKEN_TYPE_FIELD, TokenType, credentials_exception, decode_jwt
from database import SessionDep

http_bearer = HTTPBearer()


def get_current_token_payload(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> dict:
    """
    Retrieve the payload from the JWT token provided in the HTTP authorization credentials.
    """
    token = credential.credentials
    try:
        payload = decode_jwt(token)
    except Exception:
        raise credentials_exception
    return payload


async def get_current_user(
    session: SessionDep,
    payload: dict = Depends(get_current_token_payload),
) -> User:
    """
    Retrieve the current user based on the provided HTTP authorization credentials.
    """
    user = await AuthService.get_user_by_token(session, payload)

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_by_refresh(session: SessionDep, request: Request) -> User:
    """
    Retrieve the current user based on the refresh token stored in cookies.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise credentials_exception
    try:
        payload = decode_jwt(refresh_token)
    except Exception:
        raise credentials_exception

    user = await AuthService.get_user_by_token(
        session, payload, token_type=TokenType.REFRESH
    )

    if user is None:
        raise credentials_exception

    return user
