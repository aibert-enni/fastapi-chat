from fastapi import APIRouter, Depends
from shared.auth.dependencies import get_current_superuser
from app_api.users.admin_router import router as users_router

router = APIRouter(prefix="/admin")

router.dependencies = [Depends(get_current_superuser)]

router.include_router(users_router)
