import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app_api.admin.router import router as admin_router
from app_api.auth.router import router as auth_router
from app_api.chat.router import router as chat_router
from app_api.media.router import router as media_router
from app_api.push_notification.router import router as push_router
from app_api.users.router import router as users_router
from shared.database import engine
from shared.error.exception_handlers import setup_custom_exception_handlers
from shared.rabbit.rabbit_manager import rabbit_manager
from shared.settings import log_settings, settings


@asynccontextmanager
async def lifestyle(app: FastAPI):
    log_settings()
    settings.media.upload_path.mkdir(exist_ok=True)
    await rabbit_manager.connect()
    yield
    await rabbit_manager.close()
    await engine.dispose()


app = FastAPI(lifespan=lifestyle, root_path="/api")


setup_custom_exception_handlers(app)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


app.include_router(admin_router)
app.include_router(media_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(push_router)


@app.get("/")
def read_root():
    return "Hello"
