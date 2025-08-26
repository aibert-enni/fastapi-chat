from typing import Protocol


class IEmailService(Protocol):
    @staticmethod
    async def send(sender: str, to: str, subject: str, body: str) -> None: ...
