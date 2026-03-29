from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from backend.app.domain.value_objects.financial.money import Money


@dataclass
class TransactionEntity:
    """A financial transaction — either an invoice payment or a client credit adjustment.

    payment_method is set for invoice payments (e.g. "Card", "Cash", "Transfer").
    client_id is set for credit adjustments; invoice_id links to the invoice paid.
    Both may be present when a payment also generates a credit.
    """
    transaction_id: str
    amount: Money
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    invoice_id: Optional[str] = None
    client_id: Optional[str] = None
    payment_method: Optional[str] = None
    reason: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "TransactionEntity":
        raw_ts = d.get("created_at") or d.get("paid_on")
        created_at = (
            datetime.fromisoformat(raw_ts)
            if isinstance(raw_ts, str)
            else raw_ts or datetime.now(timezone.utc)
        )
        return cls(
            transaction_id=d.get("transaction_id") or d.get("payment_id", ""),
            amount=Money.of(d["amount"]),
            created_at=created_at,
            invoice_id=d.get("invoice_id"),
            client_id=d.get("client_id"),
            payment_method=d.get("payment_method"),
            reason=d.get("reason") or d.get("notes") or None,
        )

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "amount": self.amount.amount,
            "created_at": self.created_at.isoformat(),
            "invoice_id": self.invoice_id,
            "client_id": self.client_id,
            "payment_method": self.payment_method,
            "reason": self.reason,
        }
