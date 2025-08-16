from contextlib import asynccontextmanager
import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError as SQLIntegiryError,
    NoResultFound,
)

from shared.error.constants import BUSINESS_EXCEPTIONS, DATABASE_EXCEPTIONS
from shared.error.custom_exceptions import (
    DatabaseError,
    IntegrityError,
    NotFoundError,
)
from shared.settings import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.db.URL, pool_pre_ping=True, pool_recycle=3600)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_db_session():
    db = async_session()
    try:
        yield db
        await db.commit()
    except BUSINESS_EXCEPTIONS as e:
        await db.rollback()
        raise
    except DATABASE_EXCEPTIONS as e:
        await db.rollback()
        raise
    except SQLIntegiryError as e:
        await db.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        raise IntegrityError("Data integrity violation", {"original_error": str(e)})
    except NoResultFound as e:
        await db.rollback()
        logger.error(f"Database not found error: {str(e)}")
        raise NotFoundError("Data not found", {"original_error": str(e)})
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise DatabaseError("Database operation failed", {"original_error": str(e)})
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise DatabaseError("Unexpected database error", {"original_error": str(e)})
    finally:
        await db.close()


async def get_session() -> AsyncSession:
    async with get_db_session() as session:
        yield session


@asynccontextmanager
async def session_context():
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
