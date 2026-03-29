from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.ClientEntity


class Client:
    @staticmethod
    def get_all():
        return (
            DatabaseConnection().client
            .table("client")
            .select("*, person(*)")
            .execute()
            .data
        )

    @staticmethod
    def list(page: int = 1, page_size: int = 20, search: str = None):
        offset = (page - 1) * page_size
        q = DatabaseConnection().client.table("client").select("*, person!inner(*)", count="exact")
        if search:
            q = q.ilike("person.name", f"%{search}%")
        result = q.range(offset, offset + page_size - 1).execute()
        return result.data, result.count

    @staticmethod
    def get(client_id):
        return (
            DatabaseConnection().client
            .table("client")
            .select("*, person(*)")
            .eq("client_id", client_id)
            .execute()
            .data
        )

    @staticmethod
    def get_students(client_id):
        return (
            DatabaseConnection().client
            .table("student")
            .select("*, person(*)")
            .eq("client_id", client_id)
            .execute()
            .data
        )

    @staticmethod
    def get_pending_invoices(client_id):
        return (
            DatabaseConnection().client
            .table("invoice")
            .select("*")
            .eq("client_id", client_id)
            .eq("status", "Pending")
            .order("period_start")
            .execute()
            .data
        )

    @staticmethod
    def update_credits(client_id, new_balance: float):
        return (
            DatabaseConnection().client
            .table("client")
            .update({"credits": round(new_balance, 2)})
            .eq("client_id", client_id)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("client").insert(data).execute().data

    @staticmethod
    def update(client_id, data):
        return (
            DatabaseConnection().client
            .table("client")
            .update(data)
            .eq("client_id", client_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(client_id):
        return (
            DatabaseConnection().client
            .table("client")
            .delete()
            .eq("client_id", client_id)
            .execute()
            .data
        )
