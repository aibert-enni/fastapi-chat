from fastapi import HTTPException
from typing import Any, Dict, Optional


class DatabaseError(Exception):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConnectionError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


class NotFoundError(DatabaseError):
    pass


class CredentialError(Exception):
    def __init__(self, message: str = "Invalid credentials", *args):
        self.message = message
        super().__init__(self.message)


class AuthorizationError(Exception):
    def __init__(
        self, message: str = "You don't have permission to access this resource.", *args
    ):
        self.message = message
        super().__init__(*args)


class ValidationError(Exception):
    def __init__(self, message: str, *args):
        self.message = message
        super().__init__(*args)
