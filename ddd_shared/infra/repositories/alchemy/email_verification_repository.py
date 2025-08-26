from sqlalchemy import select
from sqlalchemy.exc import IntegrityError as SAIntegrityError

from ddd_shared.application.mappers.email_verification import EmailVerificationMapper
from ddd_shared.infra.domain.enteties.email_verification import EmailVerification
from ddd_shared.infra.domain.repositories.email_repository import (
    IEmailVerificationRepository,
)
from ddd_shared.infra.domain.repositories.exceptions import IntegrityError
from ddd_shared.infra.repositories.alchemy.base import BaseSQLAlchemyRepository
from shared.auth.models import EmailVerification as DBEmailVerification


class EmailVerificationRepository(
    BaseSQLAlchemyRepository, IEmailVerificationRepository
):
    async def save(self, email_verification: EmailVerification) -> EmailVerification:
        db_email_verification = EmailVerificationMapper.to_db(email_verification)
        self.session.add(db_email_verification)
        print(db_email_verification.user_id)
        await self.session.flush()
        try:
            await self.session.refresh(db_email_verification)
        except SAIntegrityError:
            raise IntegrityError(message="User already have email verification")
        return EmailVerificationMapper.to_domain(db_email_verification)

    async def get_email_verification_by_user_id(self, user_id):
        stmt = select(DBEmailVerification).where(DBEmailVerification.user_id == user_id)
        result = await self.session.execute(stmt)
        db_email_verification = result.scalar_one_or_none()
        if db_email_verification:
            return EmailVerificationMapper.to_domain(db_email_verification)
        return None
