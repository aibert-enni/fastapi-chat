from pydantic import BaseModel
from users.schemas import UserUsernameS


class UserAuthenticateS(UserUsernameS):
    password: str


class TokenS(BaseModel):
    access_token: str
    token_type: str = "bearer"
