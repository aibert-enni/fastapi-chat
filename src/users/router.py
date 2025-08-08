from fastapi import APIRouter

from database import SessionDep
from users.schemas import UserS
from users.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
async def get_user_by_id(user_id: str, session: SessionDep) -> UserS:
    db_user = await UserService.get_user_by_id(session, user_id)
    return db_user
