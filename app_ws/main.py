import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from shared.settings import settings, print_settings
from shared.database import engine
from .rabbit_manager import rabbit_manager
from .rabbit_consumer import rabbit_consumer
from .router import router


@asynccontextmanager
async def lifestyle(app: FastAPI):
    print_settings()
    settings.media.upload_path.mkdir(exist_ok=True)
    await rabbit_manager.connect()
    asyncio.create_task(rabbit_consumer.consume())
    try:
        yield
    finally:
        await rabbit_manager.close()
        await engine.dispose()


app = FastAPI(lifespan=lifestyle)

app.include_router(router)
