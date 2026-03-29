class ValidationError(Exception):
    """Raised when request data fails field-level validation. Carries a list of
    per-field error dicts: [{"field": "name", "message": "name is required."}]"""

    def __init__(self, errors: list):
        self.errors = errors
        super().__init__("Validation failed.")


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""
    pass


class ConflictError(Exception):
    """Raised for referential integrity violations or duplicate-key errors."""
    pass
