from pydantic import BaseModel, EmailStr

from shared.auth.validators import Password
from shared.users.schemas import UserUsernameS


class UserAuthenticateS(UserUsernameS):
    password: str


class UserChangePasswordS(BaseModel):
    current_password: str
    new_password: Password


class TokenS(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EmailSendS(BaseModel):
    email: EmailStr
