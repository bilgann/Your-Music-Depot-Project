from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.TransactionEntity
# Table: credit_transaction (renamed from the original CreditTransaction repo)


class Transaction:
    @staticmethod
    def get_by_client(client_id):
        return (
            DatabaseConnection().client
            .table("credit_transaction")
            .select("*")
            .eq("client_id", client_id)
            .order("created_at", desc=True)
            .execute()
            .data
        )

    @staticmethod
    def get_by_invoice(invoice_id):
        return (
            DatabaseConnection().client
            .table("credit_transaction")
            .select("*")
            .eq("invoice_id", invoice_id)
            .order("created_at", desc=True)
            .execute()
            .data
        )

    @staticmethod
    def create(client_id: str, amount: float, reason: str, invoice_id: str = None,
               payment_method: str = None):
        row = {"client_id": client_id, "amount": amount, "reason": reason}
        if invoice_id:
            row["invoice_id"] = invoice_id
        if payment_method:
            row["payment_method"] = payment_method
        return (
            DatabaseConnection().client
            .table("credit_transaction")
            .insert(row)
            .execute()
            .data
        )
