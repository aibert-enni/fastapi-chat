import asyncio
import logging

import aioredis

from app_ws.services import chat_ws_service

from .settings import settings

logger = logging.getLogger(__name__)

stop_event = asyncio.Event()


async def redis_chat_subscribe():
    redis = aioredis.from_url(settings.redis.URL, decode_responses=True)
    pubsub = redis.pubsub()

    await pubsub.subscribe("chat_channel")

    async for message in pubsub.listen():
        data = message["data"]
        if isinstance(data, str):
            await chat_ws_service.handle_data(message["data"])


async def redis_push_notifications_subscribe():
    redis = aioredis.from_url(settings.redis.URL, decode_responses=True)
    pubsub = redis.pubsub()

    await pubsub.subscribe("push_notifications")

    async for message in pubsub.listen():
        data = message["data"]
        if isinstance(data, str):
            await chat_ws_service.handle_data(data)


async def redis_publish(channel, data):
    redis = aioredis.from_url(settings.redis.URL, decode_responses=True)
    await redis.publish(channel, data)
