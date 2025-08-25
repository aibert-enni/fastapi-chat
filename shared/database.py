import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import (
    IntegrityError as SQLIntegiryError,
    NoResultFound,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from shared.error.constants import BUSINESS_EXCEPTIONS
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
    except BUSINESS_EXCEPTIONS:
        await db.rollback()
        raise
    except DatabaseError:
        await db.rollback()
        raise
    except SQLIntegiryError as e:
        await db.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        raise IntegrityError(message="Data integrity violation")
    except NoResultFound as e:
        await db.rollback()
        logger.error(f"Database not found error: {str(e)}")
        raise NotFoundError(message="Data not found")
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise DatabaseError(message="Database operation failed")
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise DatabaseError(message="Unexpected database error")
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
