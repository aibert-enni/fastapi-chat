import pytest
from httpx import AsyncClient

from .settings import test_password, test_username
from .utils import delete_user, register_user


@pytest.mark.asyncio(loop_scope="session")
async def test_login(client: AsyncClient, admin_client: AsyncClient):
    url = "/api/auth/login"

    resp = await client.post(url, json={"username": "dasdda", "password": "3123213"})

    print("Status:", resp.status_code)
    print("Text:", resp.text)

    assert resp.status_code == 401

    data = await register_user(client, test_username, test_password)

    id = data.get("id")

    resp = await client.post(
        url, json={"username": test_username, "password": test_password}
    )

    assert resp.status_code == 200

    token = resp.json().get("access_token")

    client.headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/auth/me")

    assert resp.status_code == 200

    await delete_user(admin_client, id)


@pytest.mark.asyncio(loop_scope="session")
async def test_register(client: AsyncClient, admin_client: AsyncClient):
    url = "/api/auth/register"

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
