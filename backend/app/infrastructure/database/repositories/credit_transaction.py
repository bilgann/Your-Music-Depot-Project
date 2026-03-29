from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.TransactionEntity


class CreditTransaction:
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
    def create(client_id, amount, reason, invoice_id=None):
        row = {"client_id": client_id, "amount": amount, "reason": reason}
        if invoice_id:
            row["invoice_id"] = invoice_id
        return (
            DatabaseConnection().client
            .table("credit_transaction")
            .insert(row)
            .execute()
            .data
        )
