class RepositoryError(Exception):
    def __init__(self, message: str):
        self.message = message


class IntegrityError(RepositoryError):
    def __init__(self, message: str = "Data integrity violation"):
        super().__init__(message)


class NotFoundError(RepositoryError):
    def __init__(self, message: str = "Entity not found"):
        super().__init__(message)
