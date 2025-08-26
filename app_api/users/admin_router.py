from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, status

from ddd_shared.application.usecases.user.get import (
    GetUserByIdCommand,
    GetUserByIdUseCase,
)
from shared.database import SessionDep
from shared.users.schemas import SuperUserCreateS, SuperUserS, SuperUserUpdateS
from shared.users.services import UserService

router = APIRouter(prefix="/users", tags=["admin users"], route_class=DishkaRoute)


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str, usecase: FromDishka[GetUserByIdUseCase]
) -> SuperUserS:
    command = GetUserByIdCommand(user_id)
    result = await usecase.act(command)
    return result


@router.post("/")
async def create_user(user_data: SuperUserCreateS, session: SessionDep) -> SuperUserS:
    db_user = await UserService.create_user(session, user_data)
    return db_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: str, session: SessionDep):
    """
    Delete a user by ID. Only accessible to superusers.
    """
    db_user = await UserService.get_user_by_id(session, user_id)
    await UserService.delete_user(session, db_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{user_id}")
async def update_user(
    user_id: str, user_data: SuperUserUpdateS, session: SessionDep
) -> SuperUserS:
    db_user = await UserService.get_user_by_id(session, user_id)
    db_user = await UserService.update_user(session, db_user, user_data)
    return db_user
