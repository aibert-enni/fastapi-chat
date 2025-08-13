import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi import Query
from fastapi.websockets import WebSocketState

from shared.auth.services import AuthService

from .utils import parse_ws_message
from .ws_manager import manager
from .rabbit_consumer import rabbit_consumer
from .rabbit_manager import rabbit_manager
from shared.auth.utils import decode_jwt, credentials_exception
from shared.database import SessionDep


router = APIRouter(prefix="/ws", tags=["ws"])

logger = logging.getLogger(__name__)


@router.websocket("/")
async def websocket_chat(
    websocket: WebSocket,
    session: SessionDep,
    token: str = Query(...),
):
    try:
        payload = decode_jwt(token)
    except Exception:
        raise credentials_exception

    user = await AuthService.get_user_by_token(session, payload)

    await manager.connect(user.id, websocket)
    try:
        while True:
            try:
                data = await websocket.receive_json()
                parse_ws_message(data)
                data["user_id"] = str(user.id)
                await rabbit_manager.publish_message(data, rabbit_consumer.queue_name)
            except ValueError as e:
                logger.error(f"Websocket data receive error: {e}")
    except Exception as e:
        logger.error(f"Disconnected: {e}")
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close(code=1001)
            except WebSocketDisconnect:
                pass
        manager.disconnect(websocket, user.id)
