from typing import AsyncGenerator
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from src.main import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[TestClient, None]:
    host, port = "127.0.0.1", "9000"

    async with AsyncClient(
        transport=ASGITransport(app=app, client=(host, port)), base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_register(client: TestClient):
    resp = await client.post(
        "/auth/register",
        json={"username": "chert", "fullname": "Test User", "password": "Test!1234"},
    )

    assert resp.status_code == 201

    user = 