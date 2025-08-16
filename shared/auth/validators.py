from typing import Annotated

from pydantic import AfterValidator
from pydantic_core import PydanticCustomError


def password_validator(value: str) -> str:
    if len(value) < 8:
        raise PydanticCustomError(
            "password_length", "The password must be at least 8 characters long."
        )

    has_upper = any(c.isupper() for c in value)
    has_lower = any(c.islower() for c in value)
    has_digit = any(c.isdigit() for c in value)
    has_special = any(c in '!@#$%^&*(),.?":{}|<>' for c in value)

    if not has_upper:
        raise PydanticCustomError(
            "password_upper", "The password must contain at least one capital letter."
        )
    if not has_lower:
        raise PydanticCustomError(
            "password_lower", "The password must contain at least one lowercase letter."
        )
    if not has_digit:
        raise PydanticCustomError(
            "password_digit", "The password must contain at least one digit."
        )
    if not has_special:
        raise PydanticCustomError(
            "password_special",
            "The password must contain at least one special character.",
        )

    return value


Password = Annotated[str, AfterValidator(password_validator)]
