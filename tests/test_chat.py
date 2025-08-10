import json
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
import websockets

from auth.utils import create_access_token
from chat.services import ChatService
from tests.utils import subscribe_websockets_to_chat

from .fixtures import test_engine, test_session, client
from .settings import host, port
from users.services import UserService
from users.schemas import UserCreateS


@pytest.mark.asyncio(loop_scope="session")
async def test_ws(test_session: AsyncSession):
    user1 = await UserService.create_user(
        test_session, UserCreateS(username="test1", password="1290!Qwer")
    )

    token1 = create_access_token({"sub": user1.username})

    user2 = await UserService.create_user(
        test_session, UserCreateS(username="test2", password="1290!Qwer")
    )

    token2 = create_access_token({"sub": user2.username})

    chat = await ChatService.create_private_chat(test_session, user1, user2)

    chat_id = str(chat.id)

    ws_url = lambda token: f"ws://{host}:{port}/chats/ws?token={token}"

    async with (
        websockets.connect(ws_url(token1)) as ws1,
        websockets.connect(ws_url(token2)) as ws2,
    ):
        await ws1.send(
            json.dumps(
                {
                    "action": "dasdsad",
                }
            )
        )

        response = json.loads(await ws1.recv())

        assert response.get("error") == "Unknown action: dasdsad"

        await ws1.send(
            json.dumps(
                {
                    "action": "subscribe",
                    "chat_ids": ["c3f2571c-e7ae-4564-bb7a-f7ec216ae2b9"],
                }
            )
        )

        response = json.loads(await ws1.recv())

        assert response.get("results")[0].get("status") == "error"

        await ws1.send(
            json.dumps(
                {
                    "action": "message",
                    "chat_id": "c3f2571c-e7ae-4564-bb7a-f7ec216ae2b9",
                    "text": "hello",
                }
            )
        )

        response = json.loads(await ws1.recv())

        assert response.get("status") == "error"

        await subscribe_websockets_to_chat([ws1, ws2], [chat_id])

        await ws1.send(
            json.dumps(
                {
                    "action": "message",
                    "chat_id": chat_id,
                    "text": "hello",
                }
            )
        )

        response = json.loads(await ws2.recv())

        assert response.get("message") == "hello"
        assert response.get("from") == user1.username

        await ws2.send(
            json.dumps(
                {
                    "action": "message",
                    "chat_id": chat_id,
                    "text": "dsada",
                }
            )
        )

        response = json.loads(await ws1.recv())  # to skip own message
        response = json.loads(await ws1.recv())

        print(response)

        assert response.get("message") == "dsada"
        assert response.get("from") == user2.username
