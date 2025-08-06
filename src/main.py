from contextlib import asynccontextmanager

from fastapi import FastAPI

from settings import print_settings
from database import engine

from auth.router import router as users_router


@asynccontextmanager
async def lifestyle(app: FastAPI):
    print_settings()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifestyle)

from core import exception_handlers

app.include_router(users_router)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}
