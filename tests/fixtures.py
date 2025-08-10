from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.models import Base
from src.main import app
from .settings import host, port, test_db_url


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        test_db_url,
    )

    async with engine.begin() as conn:
        # создаём таблицы
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_session(test_engine):
    async_session = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await session.rollback()


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:

    async with AsyncClient(
        transport=ASGITransport(app=app, client=(host, port)), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def admin_token(client: AsyncClient) -> str:
    response = await client.post(
        "/auth/login", json={"username": "admin", "password": "1234!Qwer"}
    )
    token = response.json()["access_token"]
    return token


@pytest_asyncio.fixture(scope="session")
async def admin_client(admin_token: str) -> AsyncGenerator[AsyncClient, None]:

    async with AsyncClient(
        transport=ASGITransport(app=app, client=(host, port)),
        base_url="http://test",
        headers={"Authorization": f"Bearer {admin_token}"},
    ) as client:
        yield client
