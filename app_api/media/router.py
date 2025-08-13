from fastapi import APIRouter, File, UploadFile

from shared.auth.dependencies import GetCurrentUserDep
from shared.database import SessionDep
from shared.media.services import MediaService

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
