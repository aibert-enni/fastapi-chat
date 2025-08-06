from typing import Optional

from sqlalchemy import String

from sqlalchemy.orm import Mapped, mapped_column

from core.models import BaseUUID


class User(BaseUUID):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    fullname: Mapped[Optional[str]]

    password: Mapped[str] = mapped_column(String(128))

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, name={self.username!r}, fullname={self.fullname!r})"
        )
