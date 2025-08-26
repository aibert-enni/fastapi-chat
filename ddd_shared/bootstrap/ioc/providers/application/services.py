from dishka import Provider, Scope, provide

from ddd_shared.application.interfaces.email_service import IEmailService
from ddd_shared.infra.services.gmail_email_service import GmailEmailService


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def email_service(self) -> IEmailService:
        service = GmailEmailService()
        return service
