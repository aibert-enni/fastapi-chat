from ddd_shared.application.interfaces.email_service import IEmailService
from ddd_shared.infra.celery.tasks.email_task import send_email


class GmailEmailService(IEmailService):
    @staticmethod
    async def send(sender: str, to: str, subject: str, body: str):
        send_email.delay(sender, to, subject, body)
