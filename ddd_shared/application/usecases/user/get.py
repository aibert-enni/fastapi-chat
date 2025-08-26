from dataclasses import dataclass

from ddd_shared.application.mappers.user import UserMapper
from ddd_shared.application.usecases.base import BaseCommand, BaseUseCase
from ddd_shared.application.usecases.user.results import UserResult
from ddd_shared.infra.domain.repositories.user_repository import IUserRepository
from shared.error.custom_exceptions import NotFoundError


@dataclass
class GetUserByIdCommand(BaseCommand):
    id: str


class GetUserByIdUseCase(BaseUseCase):
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def act(self, command: GetUserByIdCommand) -> UserResult:
        user = await self.user_repo.get_user_by_id(command.id)

        if not user:
            raise NotFoundError(message="User not found")

        return UserMapper.to_result(user)


@dataclass
class GetUserByUsernameCommand(BaseCommand):
    username: str


class GetUserByUsernameUseCase(BaseUseCase):
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def act(self, command: GetUserByUsernameCommand) -> UserResult:
        user = await self.user_repo.get_user_by_username(command.username)

        if not user:
            raise NotFoundError(message="User not found")

        return UserMapper.to_result(user)


@dataclass
class GetUserByEmailCommand(BaseCommand):
    email: str


class GetUserByEmailUseCase(BaseUseCase):
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def act(self, command: GetUserByEmailCommand) -> UserResult:
        user = await self.user_repo.get_user_by_email(command.email)

        if not user:
            raise NotFoundError(message="User not found")

        return UserMapper.to_result(user)
