from uuid import UUID
from pydantic import BaseModel

from auth.validators import Password


class UserUsernameS(BaseModel):
    username: str


class UserBaseS(UserUsernameS):
    fullname: str | None = None


class UserCreateS(UserBaseS):
    password: Password


class UserReadS(UserBaseS):

    class Config:
        from_attributes = True


class UserS(UserBaseS):
    id: UUID

    class Config:
        from_attributes = True


class SuperUserS(UserS):
    is_superuser: bool

    class Config:
        from_attributes = True


class SuperUserUpdateS(UserBaseS):
    is_superuser: bool


class SuperUserCreateS(UserCreateS):
    is_superuser: bool
