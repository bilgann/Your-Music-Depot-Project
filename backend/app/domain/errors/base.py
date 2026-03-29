"""
Base domain error codes and default messages.

Use-case: looked up by exception classes for their default message and by the
API layer when serialising error responses to the client.
"""

VALIDATION_FAILED = "VALIDATION_FAILED"
NOT_FOUND         = "NOT_FOUND"
CONFLICT          = "CONFLICT"

MESSAGES: dict[str, str] = {
    VALIDATION_FAILED: "One or more fields failed validation.",
    NOT_FOUND:         "The requested resource was not found.",
    CONFLICT:          "A business-rule conflict prevented the operation.",
}
