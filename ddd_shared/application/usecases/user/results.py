from dataclasses import dataclass
from uuid import UUID

from ddd_shared.application.usecases.base import BaseResult


@dataclass
class UserResult(BaseResult):
    id: UUID
    username: str
    fullname: str
    email: str
    is_active: str
    is_superuser: str
