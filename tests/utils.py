import json
from fastapi.testclient import TestClient
from websockets import ClientConnection


async def register_user(client: TestClient, username: str, password: str) -> dict:
    resp = await client.post(
        "/auth/register",
        json={"username": username, "fullname": "Test User", "password": password},
    )

    assert resp.status_code == 201

    return resp.json()


async def delete_user(admin_client: TestClient, id: str):
    resp = await admin_client.delete(f"/admin/users/{id}")

    assert resp.status_code == 204


async def subscribe_websockets_to_chat(
    websockets: list[ClientConnection], chat_ids: list[int]
):
    for ws in websockets:
        await ws.send(
            json.dumps(
                {
                    "action": "subscribe",
                    "chat_ids": chat_ids,
                }
            )
        )

        response = json.loads(await ws.recv())

        assert not any(
            chat.get("status") == "error" for chat in response.get("results")
        )
