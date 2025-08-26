from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from ddd_shared.application.usecases.base import BaseCommand, BaseUseCase
from ddd_shared.infra.domain.enteties.email_verification import EmailVerification
from ddd_shared.infra.domain.exceptions import DuplicationError
from ddd_shared.infra.domain.repositories.email_repository import (
    IEmailVerificationRepository,
)
from ddd_shared.infra.domain.repositories.exceptions import IntegrityError
from shared.settings import CommonSettings


@dataclass
class EmailVerificationCreateCommand(BaseCommand):
    user_id: UUID
    token_hash: str


class EmailVerificationCreateUseCase(BaseUseCase):
    def __init__(
        self,
        email_verification_repo: IEmailVerificationRepository,
        settings: CommonSettings,
    ):
        self.email_verification_repo = email_verification_repo
        self.settings = settings

    async def act(self, command: EmailVerificationCreateCommand) -> EmailVerification:
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.email.EXPIRE_MINUTES
        )
        send_at = datetime.now(timezone.utc)
        email_verification = EmailVerification(
            user_id=command.user_id,
            token_hash=command.token_hash,
            expires_at=expires_at,
            sent_at=send_at,
            is_used=False,
        )

        try:
            email_verification = await self.email_verification_repo.save(
                email_verification
            )
        except IntegrityError as e:
            raise DuplicationError(e.message)
