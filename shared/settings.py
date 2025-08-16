import json
import logging
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("uvicorn")


class MediaSettings(BaseModel):
    upload_path: Path = BASE_DIR / "uploads"


class DBSettings(BaseModel):
    URL: str


class RMQSettings(BaseModel):
    URL: str


class RedisSettings(BaseModel):
    URL: str


class JwtSettings(BaseModel):
    PRIVATE_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-private.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-public.pem"
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_nested_delimiter="__",
    )
    db: DBSettings
    rmq: RMQSettings
    redis: RedisSettings
    jwt: JwtSettings = JwtSettings()
    media: MediaSettings = MediaSettings()


settings = Settings()


def log_settings():
    logger.info("Loaded settings:\n" + settings.model_dump_json(indent=2))
