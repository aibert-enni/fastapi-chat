from dataclasses import dataclass
from typing import Protocol


@dataclass
class BaseCommand(Protocol): ...


@dataclass
class BaseResult(Protocol): ...


class BaseUseCase(Protocol):
    async def act(self, command: BaseCommand) -> BaseResult: ...
