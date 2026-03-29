class AppError(Exception):
    """Base for all application-defined exceptions."""
    pass


class DomainError(AppError):
    """Business rule violation. Safe to expose message/errors to the client."""
    pass


class ApplicationError(AppError):
    """Service or orchestration failure. Returns generic 500 to the client."""
    pass


class InfrastructureError(AppError):
    """DB or external system failure. Returns generic 500 to the client."""
    pass


class APIError(AppError):
    """HTTP boundary error. Returns generic 500 to the client."""
    pass
