from fastapi import HTTPException

from shared.error.custom_exceptions import (
    CredentialError,
    AuthorizationError,
    DatabaseError,
    NotFoundError,
    IntegrityError,
    ValidationError,
)


BUSINESS_EXCEPTIONS = (
    HTTPException,
    CredentialError,
    AuthorizationError,
    ValidationError,
)

DATABASE_EXCEPTIONS = (DatabaseError, NotFoundError, IntegrityError)
