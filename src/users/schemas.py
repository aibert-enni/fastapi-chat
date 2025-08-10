from uuid import UUID
from pydantic import BaseModel, ConfigDict

from auth.validators import Password


class UserUsernameS(BaseModel):
    username: str


class UserBaseS(UserUsernameS):
    fullname: str | None = None


class UserCreateS(UserBaseS):
    password: Password


class UserReadS(UserBaseS):

    model_config = ConfigDict(from_attributes=True)


class UserS(UserBaseS):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class SuperUserS(UserS):
    is_superuser: bool


class SuperUserUpdateS(UserBaseS):
    is_superuser: bool


class SuperUserCreateS(UserCreateS):
    is_superuser: bool
