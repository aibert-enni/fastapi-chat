import json
import logging

import aio_pika

from shared.settings import settings

logger = logging.getLogger("uvicorn")


class RabbitManager:
    def __init__(
        self,
        url,
    ):
        self.url = url
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.Channel | None = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(settings.rmq.URL)
        self.channel = await self.connection.channel()
        logger.info("RabbitMQ connected")

    async def publish_message(self, message: dict, queue_name: str):
        if not self.channel:
            raise RuntimeError("RabbitMQ connection is not established")
        await self.channel.declare_queue(queue_name, durable=True)
        body = json.dumps(message).encode("utf-8")
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=body), routing_key=queue_name
        )

    async def handle_consume(consumer):
        try:
            await consumer()
        except Exception as e:
            logging.error(
                f"Error with consumer task: {e}",
            )

    async def close(self):
        """Закрываем соединение."""
        if self.connection:
            await self.connection.close()


rabbit_manager = RabbitManager(settings.rmq.URL)
