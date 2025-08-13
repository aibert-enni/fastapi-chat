import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from shared.settings import settings, print_settings
from shared.database import engine
from .rabbit_manager import rabbit_manager
from .rabbit_consumer import rabbit_consumer
from .redis import redis_subscribe
from .router import router


@asynccontextmanager
async def lifestyle(app: FastAPI):
    print_settings()
    settings.media.upload_path.mkdir(exist_ok=True)
    await rabbit_manager.connect()
    app.state.rabbit_task = asyncio.create_task(rabbit_consumer.consume())
    app.state.redis_task = asyncio.create_task(redis_subscribe())
    try:
        yield
    finally:
        await rabbit_manager.close()

        # Останавливаем таски
        app.state.rabbit_task.cancel()
        app.state.redis_task.cancel()

        for task in (app.state.rabbit_task, app.state.redis_task):
            try:
                await task
            except asyncio.CancelledError:
                pass

        await engine.dispose()


app = FastAPI(lifespan=lifestyle)

app.include_router(router)
