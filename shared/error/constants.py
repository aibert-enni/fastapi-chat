from fastapi import HTTPException

from shared.error.custom_exceptions import (
    AuthorizationError,
    CredentialError,
    DatabaseError,
    IntegrityError,
    NotFoundError,
    ValidationError,
)

BUSINESS_EXCEPTIONS = (
    HTTPException,
    CredentialError,
    AuthorizationError,
    ValidationError,
)

DATABASE_EXCEPTIONS = (DatabaseError, NotFoundError, IntegrityError)
