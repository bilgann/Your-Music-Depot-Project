from backend.app.application.singletons.database import DatabaseConnection


class Invoice:
    def __init__(self, invoice_id, student_id, period_start, period_end,
                 total_amount, amount_paid=0, status="Pending", client_id=None):
        self.invoice_id = invoice_id
        self.student_id = student_id
        self.client_id = client_id
        self.period_start = period_start
        self.period_end = period_end
        self.total_amount = total_amount
        self.amount_paid = amount_paid
        self.status = status

    @staticmethod
    def get_all():
        return (
            DatabaseConnection().client
            .table("invoice")
            .select("*, client(*, person(*))")
            .execute()
            .data
        )

    @staticmethod
    def get(invoice_id):
        return (
            DatabaseConnection().client
            .table("invoice")
            .select("*, client(*, person(*))")
            .eq("invoice_id", invoice_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_student(student_id):
        return (
            DatabaseConnection().client
            .table("invoice")
            .select("*, client(*, person(*))")
            .eq("student_id", student_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_client(client_id):
        return (
            DatabaseConnection().client
            .table("invoice")
            .select("*")
            .eq("client_id", client_id)
            .execute()
            .data
        )

    @staticmethod
    def get_by_student_and_period(student_id, period_start):
        return (
            DatabaseConnection().client
            .table("invoice")
            .select("invoice_id")
            .eq("student_id", student_id)
            .eq("period_start", period_start)
            .execute()
            .data
        )

    @staticmethod
    def get_pending():
        return (
            DatabaseConnection().client
            .table("invoice")
            .select("*, client(*, person(*))")
            .eq("status", "Pending")
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

    @staticmethod
    def get_line_items(invoice_id):
        return (
            DatabaseConnection().client
            .table("invoice_line")
            .select("*")
            .eq("invoice_id", invoice_id)
            .execute()
            .data
        )

    @staticmethod
    def create_line_items(line_items: list):
        return (
            DatabaseConnection().client
            .table("invoice_line")
            .insert(line_items)
            .execute()
            .data
        )
