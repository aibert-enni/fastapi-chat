from datetime import datetime, timezone

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ddd_shared.application.usecases.user.register import (
    UserRegisterCommand,
    UserRegisterUseCase,
)
from shared.auth.dependencies import GetCurrentUserByRefreshDep, GetCurrentUserDep
from shared.auth.schemas import (
    EmailSendS,
    TokenS,
    UserAuthenticateS,
    UserChangePasswordS,
)
from shared.auth.services import AuthService
from shared.auth.utils import (
    create_access_token,
    create_refresh_token,
)
from shared.database import SessionDep
from shared.error.custom_exceptions import APIError
from shared.users.schemas import UserCreateS, UserS
from shared.users.services import UserService

router = APIRouter(prefix="/auth", tags=["auth"], route_class=DishkaRoute)


@router.post("/register", status_code=201)
async def register(
    user: UserCreateS, usecase: FromDishka[UserRegisterUseCase]
) -> UserS:
    command = UserRegisterCommand(
        user.username, user.fullname, user.email, user.password
    )
    user = await usecase.act(command)
    return user


@router.post("/verification/send")
async def send_verification_email(session: SessionDep, email: EmailSendS):
    db_user = await UserService.get_user_by_email(session, email.email)
    if db_user.is_active:
        return {"status": "Success", "message": "Account already verified"}

    await AuthService.send_email_verification(session, db_user)
    return {"status": "Success"}


@router.post("/verification/{token}")
async def token_verification(token: str, session: SessionDep):
    email_verification = await AuthService.get_email_verification_by_token(
        session, token
    )
    if email_verification.is_used:
        raise APIError(
            message="This verification link has already been used",
            status_code=status.HTTP_409_CONFLICT,
            error="Conflict Error",
        )
    if email_verification.expires_at < datetime.now(timezone.utc):
        raise APIError(
            message="This verification link is expired",
            status_code=status.HTTP_410_GONE,
            error="Gone Error",
        )
    await AuthService.activate_email_verification(session, email_verification)
    await UserService.activate_user(session, email_verification.user)
    return {"status": "Success"}


@router.post("/login")
async def login(
    session: FromDishka[AsyncSession], response: Response, user: UserAuthenticateS
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
