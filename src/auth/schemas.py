from pydantic import BaseModel


class UserS(BaseModel):
    username: str


class UserCreateS(UserS):
    fullname: str | None = None
    password: str


class UserAuthenticateS(UserS):
    password: str


class UserReadS(UserS):
    fullname: str | None = None

    class Config:
        from_attributes = True


class TokenS(BaseModel):
    access_token: str
    token_type: str = "bearer"
