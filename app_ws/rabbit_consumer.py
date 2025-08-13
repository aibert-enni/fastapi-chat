import json
import logging
from uuid import UUID
from aio_pika.message import AbstractIncomingMessage
from sqlalchemy.ext.asyncio import AsyncSession

from .ws_manager import ConnectionManager, manager
from .schemas import WSMessage, WSSubscribe
from .utils import parse_ws_message
from .websocket_handlers import handle_message, handle_subscribe
from shared.database import session_context
from app_ws.rabbit_manager import RabbitManager, rabbit_manager
from shared.users.services import UserService

logger = logging.getLogger(__name__)


class RabbitConsumer:
    def __init__(
        self,
        ws_manager: ConnectionManager,
        rabbit_manager: RabbitManager,
        queue_name: str,
    ):
        self.ws_manager = ws_manager
        self.rabbit_manager = rabbit_manager
        self.queue_name = queue_name

    async def _handle_incoming_message(
        self, message: AbstractIncomingMessage, session: AsyncSession
    ):
        try:
            payload = json.loads(message.body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in RabbitMQ message: {e}")
            await message.ack()
            return

        try:
            ws_message = parse_ws_message(payload)
        except ValueError as e:
            logger.error(f"Invalid WS message format: {e}")
            await message.ack()
            return

        try:
            user = await UserService.get_user_by_id(session, UUID(ws_message.user_id))
            if not user:
                logger.warning(f"User {ws_message.user_id} not found")
                await message.ack()
                return

            if isinstance(ws_message, WSMessage):
                await handle_message(
                    user,
                    session,
                    ws_message.model_dump(),
                    self.ws_manager,
                )
            elif isinstance(ws_message, WSSubscribe):
                await handle_subscribe(
                    user,
                    session,
                    ws_message.model_dump(),
                    self.ws_manager,
                )
            else:
                raise ValueError(f"Unknown WS message type: {type(ws_message)}")

        except Exception as e:
            logger.exception(f"Error processing RabbitMQ message: {e}")
            try:
                await self.ws_manager.send_json_to_user(
                    UUID(ws_message.user_id),
                    {
                        "status": "error",
                        "error": "Message processing failed",
                    },
                )
            except Exception as send_err:
                logger.error(f"Failed to send error message to user: {send_err}")
            if isinstance(e, ConnectionError):
                await message.nack(requeue=True)  # Temporary issue → retry
            else:
                await message.nack(requeue=False)  # Permanent issue → drop
            return

        await message.ack()

    async def consume(self):
        channel = await self.rabbit_manager.connection.channel()
        queue = await channel.declare_queue(self.queue_name, durable=True)

        async with queue.iterator() as q:
            async for message in q:
                async with session_context() as session:
                    await self._handle_incoming_message(message, session)


rabbit_consumer = RabbitConsumer(manager, rabbit_manager, "chat_events")
