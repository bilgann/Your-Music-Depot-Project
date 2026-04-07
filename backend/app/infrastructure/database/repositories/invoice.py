from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.InvoiceEntity


class Invoice:
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
        """
        Bulk-insert invoice line items.
        Each dict must include: invoice_id, description, amount, item_type.
        lesson_id and attendance_status are optional (lesson items only).
        """
        return (
            DatabaseConnection().client
            .table("invoice_line")
            .insert(line_items)
            .execute()
            .data
        )
