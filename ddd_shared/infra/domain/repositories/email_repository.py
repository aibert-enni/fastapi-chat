from typing import Optional, Protocol
from uuid import UUID

from ddd_shared.infra.domain.enteties.email_verification import EmailVerification


class IEmailVerificationRepository(Protocol):
    async def save(
        self, email_verification: EmailVerification
    ) -> EmailVerification: ...

    async def get_email_verification_by_user_id(
        self, user_id: UUID
    ) -> Optional[EmailVerification]: ...
