from dataclasses import dataclass

from ddd_shared.application.usecases.base import BaseCommand, BaseUseCase
from ddd_shared.application.usecases.user.results import UserResult
from ddd_shared.application.utils.user import hash_password
from ddd_shared.infra.domain.enteties.user import User
from ddd_shared.infra.domain.exceptions import DuplicationError
from ddd_shared.infra.domain.repositories.exceptions import IntegrityError
from ddd_shared.infra.domain.repositories.user_repository import IUserRepository


@dataclass
class UserCreateByRegisterCommand(BaseCommand):
    username: str
    fullname: str
    email: str
    password: str


class UserCreateByRegisterUseCase(BaseUseCase):
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def act(self, command: UserCreateByRegisterCommand) -> UserResult:
        hashed_password = hash_password(command.password)
        user = User(command.username, command.fullname, command.email, hashed_password)
        try:
            user = await self.user_repo.save(user)
        except IntegrityError as e:
            raise DuplicationError(e.message)
        return user
