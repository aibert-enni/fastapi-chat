from fastapi import APIRouter, Depends, Response

from auth.services import AuthService
from auth.utils import (
    TokenType,
    create_access_token,
    create_refresh_token,
    credentials_exception,
)
from auth.dependencies import get_current_user, get_current_user_by_refresh
from database import SessionDep
from auth.schemas import TokenS, UserAuthenticateS, UserCreateS, UserReadS

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(session: SessionDep, user: UserCreateS) -> UserReadS:
    user = await AuthService.create_user(session, user)
    return UserReadS.model_validate(user)


@router.post("/login")
async def login(
    session: SessionDep, response: Response, user: UserAuthenticateS
) -> TokenS:
    user = await AuthService.authenticate_user(session, user)
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    return TokenS(access_token=access_token, token_type="bearer")


@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}


@router.post(
    "/refresh",
    response_model=TokenS,
    response_model_exclude_none=True,
)
async def refresh_token(
    current_user: dict = Depends(get_current_user_by_refresh),
) -> TokenS:

    access_token = create_access_token({"sub": current_user.username})

    return TokenS(access_token=access_token, token_type="bearer")
