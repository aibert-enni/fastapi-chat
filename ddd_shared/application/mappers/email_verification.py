from ddd_shared.application.mappers.base import BaseMapper
from ddd_shared.infra.domain.enteties.email_verification import EmailVerification
from shared.auth.models import EmailVerification as EmailVerificationDB


class EmailVerificationMapper(
    BaseMapper[EmailVerification, EmailVerificationDB, EmailVerification]
):
    domain_cls = EmailVerification
    db_cls = EmailVerificationDB
    result_cls = EmailVerification

    @classmethod
    def to_domain(cls, db_model: EmailVerificationDB) -> EmailVerification:
        return EmailVerification(
            user_id=db_model.user_id,
            token_hash=db_model.token_hash,
            expires_at=db_model.expires_at,
            sent_at=db_model.sent_at,
            is_used=db_model.is_used,
            id=db_model.id,
        )

    @classmethod
    def to_db(cls, domain_obj: EmailVerificationDB):
        return EmailVerificationDB(
            user_id=domain_obj.user_id,
            token_hash=domain_obj.token_hash,
            expires_at=domain_obj.expires_at,
            sent_at=domain_obj.sent_at,
            is_used=domain_obj.is_used,
        )
