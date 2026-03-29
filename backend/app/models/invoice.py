from backend.app.singletons.database import DatabaseConnection


class Invoice:
    def __init__(self, invoice_id, student_id, period_start, period_end,
                 total_amount, amount_paid=0, status="Pending"):
        self.invoice_id = invoice_id
        self.student_id = student_id
        self.period_start = period_start
        self.period_end = period_end
        self.total_amount = total_amount
        self.amount_paid = amount_paid
        self.status = status

    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("invoice").select("*").execute().data

    @staticmethod
    def get(invoice_id):
        return (
            DatabaseConnection().client
            .table("invoice")
            .select("*")
            .eq("invoice_id", invoice_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_student(student_id):
        return (
            DatabaseConnection().client
            .table("invoice")
            .select("*")
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("invoice").insert(data).execute().data

    @staticmethod
    def update(invoice_id, data):
        return (
            DatabaseConnection().client
            .table("invoice")
            .update(data)
            .eq("invoice_id", invoice_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(invoice_id):
        return (
            DatabaseConnection().client
            .table("invoice")
            .delete()
            .eq("invoice_id", invoice_id)
            .execute()
            .data
        )
