"""
Financial domain error codes and default messages.

Covers invoicing and payment business-rule violations.
"""

DUPLICATE_INVOICE        = "DUPLICATE_INVOICE"
NO_LESSONS_FOUND         = "NO_LESSONS_FOUND"
INVOICE_NOT_FOUND        = "INVOICE_NOT_FOUND"
INVOICE_CANCELLED        = "INVOICE_CANCELLED"
INVOICE_ALREADY_PAID     = "INVOICE_ALREADY_PAID"
OVERPAYMENT              = "OVERPAYMENT"
INVALID_PAYMENT_AMOUNT   = "INVALID_PAYMENT_AMOUNT"

MESSAGES: dict[str, str] = {
    DUPLICATE_INVOICE:      "An invoice for this student and period already exists.",
    NO_LESSONS_FOUND:       "No qualifying lessons were found for the requested invoice period.",
    INVOICE_NOT_FOUND:      "The target invoice does not exist.",
    INVOICE_CANCELLED:      "Cannot apply payment — the invoice has been cancelled.",
    INVOICE_ALREADY_PAID:   "Cannot apply payment — the invoice is already fully paid.",
    OVERPAYMENT:            "Payment amount exceeds the outstanding balance.",
    INVALID_PAYMENT_AMOUNT: "Payment amount must be greater than zero.",
}
