from fastapi import status


class DatabaseError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error: str = "API Error",
    ):
        self.message = message
        self.status_code = status_code
        self.error = error


class IntegrityError(DatabaseError):
    def __init__(
        self,
        message,
        status_code=status.HTTP_400_BAD_REQUEST,
        error="Data Validation Error",
    ):
        super().__init__(message, status_code, error)


class NotFoundError(DatabaseError):
    def __init__(
        self,
        message,
        status_code=status.HTTP_404_NOT_FOUND,
        error="Resource Not Found",
    ):
        super().__init__(message, status_code, error)


class APIError(Exception):
    def __init__(self, message: str, status_code: int, error: str = "API Error"):
        self.message = message
        self.status_code = status_code
        self.error = error


class CredentialError(APIError):
    def __init__(
        self,
        message: str = "Invalid credentials",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        error: str = "Credential Error",
    ):
        super().__init__(message, status_code, error)


class AuthorizationError(APIError):
    def __init__(
        self,
        message: str = "You don't have permission to access this resource.",
        status_code: int = status.HTTP_403_FORBIDDEN,
        error: str = "Authorization Error",
    ):
        super().__init__(message, status_code, error)


class ValidationError(APIError):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        error: str = "Validation Error",
    ):
        super().__init__(message, status_code, error)


class ServiceUnavailableError(APIError):
    def __init__(
        self,
        message: str = "Service unavailable",
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        error: str = "Service Unavailable Error",
    ):
        super().__init__(message, status_code, error)
