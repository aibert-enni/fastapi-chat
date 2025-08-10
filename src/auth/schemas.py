from pydantic import BaseModel
from auth.validators import Password
from users.schemas import UserUsernameS


class UserAuthenticateS(UserUsernameS):
    password: str


class UserChangePasswordS(BaseModel):
    current_password: str
    new_password: Password


class TokenS(BaseModel):
    access_token: str
    token_type: str = "bearer"
