from backend.app.domain.exceptions.exceptions import ConflictError, NotFoundError


class DuplicateInvoiceError(ConflictError):
    """Raised when an invoice for the same student and period already exists."""
    pass


class NoLessonsFoundError(NotFoundError):
    """Raised when no qualifying lessons exist for the requested invoice period."""
    pass
