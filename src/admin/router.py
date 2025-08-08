from fastapi import APIRouter, Depends
from auth.dependencies import get_current_superuser
from users.admin_router import router as users_router

router = APIRouter(prefix="/admin")

router.dependencies = [Depends(get_current_superuser)]

router.include_router(users_router)
