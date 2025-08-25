from fastapi import HTTPException

from shared.error.custom_exceptions import (
    APIError,
)

BUSINESS_EXCEPTIONS = (
    APIError,
    HTTPException,
)
