from fastapi import APIRouter, Response

from auth.services import AuthService
from auth.utils import (
    create_access_token,
    create_refresh_token,
)
from auth.dependencies import GetCurrentUserByRefreshDep, GetCurrentUserDep
from database import SessionDep
from auth.schemas import TokenS, UserAuthenticateS
from users.schemas import UserCreateS, UserS
from users.services import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(session: SessionDep, user: UserCreateS) -> UserS:
    db_user = await UserService.create_user(session, user)
    return db_user


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
def read_users_me(current_user: GetCurrentUserDep) -> UserS:
    return {"user": current_user}


@router.post(
    "/refresh",
    response_model=TokenS,
    response_model_exclude_none=True,
)
async def refresh_token(
    current_user: GetCurrentUserByRefreshDep,
) -> TokenS:

    access_token = create_access_token({"sub": current_user.username})

    return TokenS(access_token=access_token, token_type="bearer")
