from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from ddd_shared.infra.domain.repositories.email_repository import (
    IEmailVerificationRepository,
)
from ddd_shared.infra.domain.repositories.user_repository import IUserRepository
from ddd_shared.infra.repositories.alchemy.email_verification_repository import (
    EmailVerificationRepository,
)
from ddd_shared.infra.repositories.alchemy.user_repository import UserRepository


class UserRepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def user_repository(self, session: AsyncSession) -> IUserRepository:
        repository = UserRepository(session)

        return repository


class EmailVerificationRepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def email_verification_repository(
        self, session: AsyncSession
    ) -> IEmailVerificationRepository:
        repository = EmailVerificationRepository(session)
        return repository
