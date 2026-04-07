# Backward-compatibility shim.
# These exceptions now live in domain.exceptions.financial.
from backend.app.domain.exceptions.financial import DuplicateInvoiceError, NoLessonsFoundError

__all__ = ["DuplicateInvoiceError", "NoLessonsFoundError"]
