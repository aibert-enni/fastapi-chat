import logging

import asyncpg
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app_api.main import app

logger = logging.getLogger(__name__)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"IntegrityError: {str(exc)}")

    if hasattr(exc, "orig") and isinstance(
        exc.orig, asyncpg.exceptions.UniqueViolationError
    ):
        return JSONResponse(
            status_code=409,
            content={"detail": "Уже существует объект с таким уникальным значением."},
        )

    return JSONResponse(
        status_code=400, content={"detail": "Ошибка целостности базы данных."}
    )
