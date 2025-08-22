import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi import Query
from fastapi.websockets import WebSocketState
from pydantic import ValidationError

from shared.redis import redis_publish
from shared.auth.services import AuthService

from .utils import parse_ws_message
from .ws_manager import manager
from shared.auth.utils import decode_jwt
from shared.error.custom_exceptions import CredentialError
from shared.database import SessionDep


router = APIRouter(tags=["ws"])

logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    session: SessionDep,
    token: str = Query(...),
):
    try:
        payload = decode_jwt(token)
    except Exception:
        raise CredentialError

    user = await AuthService.get_user_by_token(session, payload)

    await manager.connect(user.id, websocket)
    try:
        while True:
            try:
                data = await websocket.receive_json()
                parse_ws_message(data)
                data["user_id"] = str(user.id)
                await redis_publish("chat_channel", json.dumps(data))
            except ValidationError as e:
                logger.error(f"Websocket data validation error: {e}")
                await websocket.send_json({"status": "error", "error": e.errors()})
            except ValueError as e:
                logger.error(f"Websocket action error: {e}")
                await websocket.send_json({"status": "error", "error": str(e)})
    except Exception as e:
        logger.error(f"Disconnected: {e}")
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close(code=1001)
            except WebSocketDisconnect:
                pass
        manager.disconnect(websocket, user.id)
