from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile

from auth.dependencies import GetCurrentUserDep
from database import SessionDep
from media.services import MediaService
from settings import settings

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload/image/user")
async def upload_img(
    session: SessionDep,
    current_user: GetCurrentUserDep,
    file: UploadFile = File(...),
):
    avatar = await MediaService.upload_avatar(
        session,
        owner_id=current_user.id,
        file=file,
        alt_text=f"Image of {current_user.username}",
    )
    return {"status": "success", "file path": avatar.file_path}
