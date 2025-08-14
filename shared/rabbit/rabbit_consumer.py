import json
import logging
from uuid import UUID
from aio_pika.message import AbstractIncomingMessage
from sqlalchemy.ext.asyncio import AsyncSession

from shared.redis import redis_publish
from shared.websocket.schemas import WSPushNotificationS

from shared.database import session_context
from shared.rabbit.rabbit_manager import RabbitManager, rabbit_manager
from shared.users.services import UserService

logger = logging.getLogger(__name__)


class RabbitConsumer:
    def __init__(self, rabbit_manager: RabbitManager):
        self.rabbit_manager = rabbit_manager

    async def _parse_incoming_payload(self, payload: dict):
        action = payload.get("action")
        if action == "push_notification":
            return WSPushNotificationS(**payload)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _handle_incoming_message(
        self, message: AbstractIncomingMessage, session: AsyncSession
    ):
        try:
            try:
                payload = json.loads(message.body.decode("utf-8"))

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in RabbitMQ message: {e}")
                await message.ack()
                return

            try:
                ws_message = await self._parse_incoming_payload(payload)
            except ValueError as e:
                logger.error(f"Invalid WS message format: {e}")
                await message.ack()
                return

            try:
                user = await UserService.get_user_by_id(session, ws_message.user_id)
                if not user:
                    logger.warning(f"User {ws_message.user_id} not found")
                    await message.ack()
                    return
            except Exception as e:
                logger.exception(f"Error processing RabbitMQ message: {e}")
                if isinstance(e, ConnectionError):
                    await message.nack(requeue=True)  # Temporary issue → retry
                else:
                    await message.nack(requeue=False)  # Permanent issue → drop
                return

            try:
                await redis_publish("push_notifications", ws_message.model_dump_json())
            except Exception as e:
                logger.exception(f"Error redis publishing message: {e}")
                message.ack()
        except Exception as e:
            logger.error(e)
            await message.ack()

    async def consume(self, queue_name: str):
        channel = await self.rabbit_manager.connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as q:
            async for message in q:
                async with session_context() as session:
                    await self._handle_incoming_message(message, session)


rabbit_consumer = RabbitConsumer(rabbit_manager)
