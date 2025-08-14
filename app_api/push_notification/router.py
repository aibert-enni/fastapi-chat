from uuid import UUID
from fastapi import APIRouter

from shared.database import SessionDep
from shared.push.schemas import PushCreateS
from shared.rabbit.rabbit_manager import rabbit_manager
from shared.users.services import UserService
from shared.websocket.schemas import WSPushNotificationS

router = APIRouter(prefix="/push_notification", tags=["push"])


@router.post("/{user_id}")
async def push_to_user(user_id: UUID, data: PushCreateS, session: SessionDep):
    user = await UserService.get_user_by_id(session, user_id)
    ws_data = WSPushNotificationS(
        action="push_notification", user_id=user.id, message=data.message
    )
    await rabbit_manager.publish_message(
        ws_data.model_dump(mode="json"), "push_notifications"
    )
    return {"status": "pending"}
