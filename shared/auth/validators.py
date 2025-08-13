from typing import Annotated

from pydantic import AfterValidator


def password_validator(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Пароль должен быть не менее 8 символов")

    has_upper = any(c.isupper() for c in value)
    has_lower = any(c.islower() for c in value)
    has_digit = any(c.isdigit() for c in value)
    has_special = any(c in '!@#$%^&*(),.?":{}|<>' for c in value)

    if not has_upper:
        raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
    if not has_lower:
        raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
    if not has_digit:
        raise ValueError("Пароль должен содержать хотя бы одну цифру")
    if not has_special:
        raise ValueError("Пароль должен содержать хотя бы один специальный символ")

    return value


Password = Annotated[str, AfterValidator(password_validator)]
