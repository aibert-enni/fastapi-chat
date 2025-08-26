from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from ddd_shared.application.interfaces.email_service import IEmailService
from ddd_shared.application.mappers.user import UserMapper
from ddd_shared.application.usecases.base import BaseUseCase
from ddd_shared.application.usecases.email_verification.create import (
    EmailVerificationCreateCommand,
    EmailVerificationCreateUseCase,
)
from ddd_shared.application.usecases.user.create import (
    UserCreateByRegisterCommand,
    UserCreateByRegisterUseCase,
)
from ddd_shared.application.usecases.user.results import UserResult
from ddd_shared.application.utils.auth import generate_verification_token
from ddd_shared.infra.domain.exceptions import DuplicationError
from ddd_shared.infra.domain.repositories.user_repository import IUserRepository


@dataclass
class UserRegisterCommand(UserCreateByRegisterCommand):
    pass


class UserRegisterUseCase(BaseUseCase):
    def __init__(
        self,
        user_repo: IUserRepository,
        user_create_use_case: UserCreateByRegisterUseCase,
        email_verification_create_use_case: EmailVerificationCreateUseCase,
        email_service: IEmailService,
        session: AsyncSession,
    ):
        self.user_repo = user_repo
        self.user_create_use_case = user_create_use_case
        self.email_verification_create_use_case = email_verification_create_use_case
        self.email_service = email_service
        self.session = session

    async def act(self, command: UserRegisterCommand) -> UserResult:
        async with self.session.begin():
            user = await self.user_create_use_case.act(command)
            raw, hashed = generate_verification_token()
            email_verification_create_command = EmailVerificationCreateCommand(
                user_id=user.id, token_hash=hashed
            )
            try:
                await self.email_verification_create_use_case.act(
                    email_verification_create_command
                )
            except DuplicationError:
                pass
        await self.email_service.send("POSOSI", user.email, "Email Verification", raw)
        return UserMapper.to_result(user)
