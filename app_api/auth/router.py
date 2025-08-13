from fastapi import APIRouter, Response

from shared.auth.services import AuthService
from shared.auth.utils import (
    create_access_token,
    create_refresh_token,
)
from shared.auth.dependencies import GetCurrentUserByRefreshDep, GetCurrentUserDep
from shared.database import SessionDep
from shared.auth.schemas import TokenS, UserAuthenticateS, UserChangePasswordS
from shared.users.schemas import UserCreateS, UserS
from shared.users.services import UserService

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
    return current_user


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


@router.post("/change-password")
async def change_password(
    data: UserChangePasswordS, current_user: GetCurrentUserDep, session: SessionDep
):
    await AuthService.change_user_password(
        session, current_user, data.current_password, data.new_password
    )
    return {"status": "success", "message": "Password was changed"}
