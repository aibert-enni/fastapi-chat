from typing import Optional, Protocol
from uuid import UUID

from ddd_shared.infra.domain.enteties.user import User


class IUserRepository(Protocol):
    async def save(self, user: User) -> User: ...

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]: ...

    async def get_user_by_username(self, username: str) -> Optional[User]: ...

    async def get_user_by_email(self, email: str) -> Optional[User]: ...
