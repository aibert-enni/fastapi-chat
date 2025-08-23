from fastapi import APIRouter, Depends

from app_api.users.admin_router import router as users_router
from shared.auth.dependencies import get_current_superuser

router = APIRouter(prefix="/admin")

router.dependencies = [Depends(get_current_superuser)]

router.include_router(users_router)
