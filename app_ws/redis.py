import asyncio
import json
import logging
from uuid import UUID
import aioredis

from .services import chat_ws_service
from shared.settings import settings

logger = logging.getLogger(__name__)

stop_event = asyncio.Event()


async def redis_subscribe():
    redis = aioredis.from_url(settings.redis.URL, decode_responses=True)
    pubsub = redis.pubsub()

    await pubsub.subscribe("chat_channel")

    async for message in pubsub.listen():
        print(message)
        data = message["data"]
        if isinstance(data, str):
            await chat_ws_service.handle_data(message["data"])


async def redis_publish(channel, data):
    redis = aioredis.from_url(settings.redis.URL, decode_responses=True)
    await redis.publish(channel, json.dumps(data))
