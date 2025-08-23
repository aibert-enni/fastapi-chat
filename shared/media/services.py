import logging
import shutil
from pathlib import Path
from typing import Optional, Tuple, Union
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.media.models import Image
from shared.settings import settings

logger = logging.getLogger(__name__)


class MediaService:
    @staticmethod
    def create_file(file: UploadFile, file_path: Path):
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return file
        except Exception as e:
            logger.error(e)
            return False

    @staticmethod
    def set_file_name(file: UploadFile, file_name: str) -> UploadFile:
        original_ext = Path(file.filename).suffix
        new_name = file_name + original_ext
        file.filename = new_name
        return file

    @staticmethod
    def get_file_path(folder_name: str, file_name: str):
        folder_path = settings.media.upload_path / folder_name
        folder_path.mkdir(exist_ok=True)
        file_path = folder_path / file_name
        return file_path

    @classmethod
    def add_file(
        cls, file: UploadFile, folder_name: str, file_name: Optional[str] = None
    ) -> Union[Tuple[UploadFile, str], Tuple[bool, str]]:
        if file_name:
            file = cls.set_file_name(file, file_name)

        file_path = cls.get_file_path(folder_name, file.filename)
        return cls.create_file(file, file_path), file_path

    @staticmethod
    def check_if_image(file: UploadFile):
        allowed_types = {"image/jpeg", "image/png", "image/gif"}

        if file.content_type in allowed_types:
            return True
        return False

    @classmethod
    async def upload_image(
        cls,
        session: AsyncSession,
        owner_id: UUID,
        file: UploadFile,
        owner_type: str,
        folder_name: str,
        file_name: Optional[str] = None,
        alt_text: Optional[str] = None,
    ) -> Image:
        if not cls.check_if_image(file):
            raise HTTPException(
                detail={
                    "error": "File has to be image",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if file_name:
            file = cls.set_file_name(file, file_name)

        file_path = cls.get_file_path(folder_name, file.filename)

        file_db = Image(
            owner_id=owner_id,
            owner_type=owner_type,
            file_path=str(file_path),
        )

        if alt_text:
            file_db.alt_text = alt_text

        session.add(file_db)

        try:
            await session.commit()
            await session.refresh(file_db)
            file = cls.create_file(file, file_path)
            logger.info(f"Saving file to {file_path}")
            if not file:
                raise RuntimeError(f"Failed to save file: {file.filename}")
        except Exception:
            await session.rollback()
            raise HTTPException(
                detail={"error": "Image isn't uploaded"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return file_db

    @classmethod
    async def update_image(
        cls,
        session: AsyncSession,
        db_file: Image,
        file: UploadFile,
        folder_name: str,
        file_name: Optional[str] = None,
        alt_text: Optional[str] = None,
    ):
        exist_file_path = Path(db_file.file_path)

        if exist_file_path.exists() and exist_file_path.is_file():
            try:
                exist_file_path.unlink()
                logger.info(f"Deleted old file: {exist_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete old file {exist_file_path}: {e}")

        file_result, new_file_path = cls.add_file(file, folder_name, file_name)

        if not file_result:
            raise HTTPException(
                detail={"error": "Failed to save new file"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            db_file.file_path = str(new_file_path)

            if alt_text:
                db_file.alt_text = alt_text

            await session.commit()
            await session.refresh(db_file)

            return db_file

        except Exception:
            try:
                new_file_path.unlink()
                logger.info(
                    f"Cleaned up new file due to database error: {new_file_path}"
                )
            except Exception:
                pass

            await session.rollback()
            raise HTTPException(
                detail={"error": "Failed to update image in database"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @classmethod
    async def upload_avatar(
        cls,
        session: AsyncSession,
        owner_id: UUID,
        file: UploadFile,
        alt_text: Optional[str] = None,
    ) -> Optional[Image]:
        # Убираем дублирование проверки
        if not cls.check_if_image(file):
            raise HTTPException(
                detail={"error": "File has to be image"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        existing = await session.scalar(
            select(Image).where(Image.owner_id == owner_id, Image.owner_type == "users")
        )

        owner_type = "users"
        folder_name = "users"
        file_name = str(owner_id)

        if existing:
            return await cls.update_image(
                session, existing, file, folder_name, file_name, alt_text
            )
        return await cls.upload_image(
            session,
            owner_id,
            file,
            owner_type=owner_type,
            folder_name=folder_name,
            file_name=file_name,
            alt_text=alt_text,
        )
