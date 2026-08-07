class ApplicationError(Exception):
    """Base exception for expected application failures."""


class ConflictError(ApplicationError):
    pass


class AuthenticationError(ApplicationError):
    pass


class NotFoundError(ApplicationError):
    pass


class ValidationError(ApplicationError):
    pass