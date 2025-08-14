from pydantic import BaseModel


class PushCreateS(BaseModel):
    message: str
