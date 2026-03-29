from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.TransactionEntity


class Payment:
    @staticmethod
    def get_all():
        return (
            DatabaseConnection().client
            .table("payment")
            .select("*, invoice(client_id, student_id, period_start, period_end, client(*, person(*)))")
            .execute()
            .data
        )

    @staticmethod
    def list(page: int = 1, page_size: int = 20):
        offset = (page - 1) * page_size
        result = (
            DatabaseConnection().client
            .table("payment")
            .select("*, invoice(client_id, student_id, period_start, period_end, client(*, person(*)))", count="exact")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        return result.data, result.count

    @staticmethod
    def get(payment_id):
        return (
            DatabaseConnection().client
            .table("payment")
            .select("*, invoice(client_id, student_id, period_start, period_end, client(*, person(*)))")
            .eq("payment_id", payment_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_invoice(invoice_id):
        return (
            DatabaseConnection().client
            .table("payment")
            .select("*")
            .eq("invoice_id", invoice_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_client(client_id):
        invoices = (
            DatabaseConnection().client
            .table("invoice")
            .select("invoice_id")
            .eq("client_id", client_id)
            .execute()
            .data
        )
        invoice_ids = [inv["invoice_id"] for inv in invoices]
        if not invoice_ids:
            return []
        return (
            DatabaseConnection().client
            .table("payment")
            .select("*")
            .in_("invoice_id", invoice_ids)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("payment").insert(data).execute().data

    @staticmethod
    def delete(payment_id):
        return (
            DatabaseConnection().client
            .table("payment")
            .delete()
            .eq("payment_id", payment_id)
            .execute()
            .data
        )
