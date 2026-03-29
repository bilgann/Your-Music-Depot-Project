from backend.app.singletons.database import DatabaseConnection


class Payment:
    def __init__(self, payment_id, invoice_id, amount, payment_method="Card", paid_on=None, notes=""):
        self.payment_id = payment_id
        self.invoice_id = invoice_id
        self.amount = amount
        self.payment_method = payment_method
        self.paid_on = paid_on
        self.notes = notes

    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("payment").select("*").execute().data

    @staticmethod
    def get(payment_id):
        return (
            DatabaseConnection().client
            .table("payment")
            .select("*")
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
