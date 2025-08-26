from dishka import Provider, Scope, provide

from ddd_shared.application.usecases.email_verification.create import (
    EmailVerificationCreateUseCase,
)
from ddd_shared.infra.domain.repositories.email_repository import (
    IEmailVerificationRepository,
)
from shared.settings import CommonSettings


class EmailVerificationUseCasesProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def email_verification_create(
        self,
        email_verification_repository: IEmailVerificationRepository,
        settings: CommonSettings,
    ) -> EmailVerificationCreateUseCase:
        usecase = EmailVerificationCreateUseCase(
            email_verification_repository, settings
        )

        return usecase
