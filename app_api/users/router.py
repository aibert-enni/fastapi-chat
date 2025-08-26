from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from ddd_shared.application.usecases.user.get import (
    GetUserByIdCommand,
    GetUserByIdUseCase,
)
from shared.users.schemas import UserS

router = APIRouter(prefix="/users", tags=["users"], route_class=DishkaRoute)


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str, usecase: FromDishka[GetUserByIdUseCase]
) -> UserS:
    command = GetUserByIdCommand(user_id)
    result = await usecase.act(command)
    return result
