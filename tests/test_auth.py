from httpx import AsyncClient
import pytest
from .utils import delete_user, register_user

from .settings import test_username, test_password

from .fixtures import client, admin_token, admin_client


@pytest.mark.asyncio(loop_scope="session")
async def test_login(client: AsyncClient, admin_client: AsyncClient):
    url = "/auth/login"

    resp = await client.post(url, json={"username": "dasdda", "password": "3123213"})

    assert resp.status_code == 404

    data = await register_user(client, test_username, test_password)

    id = data.get("id")

    resp = await client.post(
        url, json={"username": test_username, "password": test_password}
    )

    assert resp.status_code == 200

    token = resp.json().get("access_token")

    client.headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/auth/me")

    assert resp.status_code == 200

    await delete_user(admin_client, id)


@pytest.mark.asyncio(loop_scope="session")
async def test_register(client: AsyncClient, admin_client: AsyncClient):
    url = "/auth/register"

    resp = await client.post(
        url,
        json={"username": test_username, "fullname": "Test User", "password": "dasdas"},
    )

    assert resp.status_code == 422

    resp = await client.post(
        url,
        json={
            "username": test_username,
            "fullname": "Test User",
            "password": test_password,
        },
    )

    assert resp.status_code == 201

    id = resp.json().get("id")

    await delete_user(admin_client, id)
