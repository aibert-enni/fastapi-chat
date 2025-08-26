from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class User:
    username: str
    fullname: str
    email: str
    password: str
    is_active: bool = False
    is_superuser: bool = False
    id: Optional[UUID] = None
