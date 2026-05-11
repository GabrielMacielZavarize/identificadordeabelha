class AppError(Exception):
    """Base application exception."""


class NotFoundError(AppError):
    """Raised when an entity cannot be found."""


class ConflictError(AppError):
    """Raised when an entity violates uniqueness constraints."""


class InvalidRequestError(AppError):
    """Raised when request input is invalid."""


class ModelNotReadyError(AppError):
    """Raised when the active model is missing or unusable."""
