from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from ddd_shared.application.interfaces.email_service import IEmailService
from ddd_shared.application.usecases.email_verification.create import (
    EmailVerificationCreateUseCase,
)
from ddd_shared.application.usecases.user.create import UserCreateByRegisterUseCase
from ddd_shared.application.usecases.user.get import (
    GetUserByEmailUseCase,
    GetUserByIdUseCase,
    GetUserByUsernameUseCase,
)
from ddd_shared.application.usecases.user.register import UserRegisterUseCase
from ddd_shared.infra.domain.repositories.user_repository import IUserRepository


class UserUseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def user_get_by_id(self, user_repository: IUserRepository) -> GetUserByIdUseCase:
        usecase = GetUserByIdUseCase(user_repository)
        return usecase

    @provide
    def user_get_by_username(
        self, user_repository: IUserRepository
    ) -> GetUserByUsernameUseCase:
        usecase = GetUserByUsernameUseCase(user_repo=user_repository)
        return usecase

    @provide
    def user_get_by_email(
        self, user_repository: IUserRepository
    ) -> GetUserByEmailUseCase:
        usecase = GetUserByEmailUseCase(user_repo=user_repository)
        return usecase

    @provide
    def user_create_by_register(
        self, user_repository: IUserRepository
    ) -> UserCreateByRegisterUseCase:
        usecase = UserCreateByRegisterUseCase(user_repo=user_repository)
        return usecase

    @provide
    def user_register(
        self,
        user_repo: IUserRepository,
        user_create_use_case: UserCreateByRegisterUseCase,
        email_verification_create_use_case: EmailVerificationCreateUseCase,
        email_service: IEmailService,
        session: AsyncSession,
    ) -> UserRegisterUseCase:
        usecase = UserRegisterUseCase(
            user_repo,
            user_create_use_case,
            email_verification_create_use_case,
            email_service,
            session,
        )
        return usecase
