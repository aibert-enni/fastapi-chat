from fastapi import status


class DomainError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error: str = "API Error",
    ):
        self.message = message
        self.status_code = status_code
        self.error = error


class DuplicationError(DomainError):
    def __init__(
        self,
        message,
        status_code=status.HTTP_400_BAD_REQUEST,
        error="Data Validation Error",
    ):
        super().__init__(message, status_code, error)


class NotFoundError(DomainError):
    def __init__(
        self,
        message,
        status_code=status.HTTP_404_NOT_FOUND,
        error="Resource Not Found",
    ):
        super().__init__(message, status_code, error)
