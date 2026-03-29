from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.PersonEntity


class Person:
    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("person").select("*").execute().data

    @staticmethod
    def get(person_id):
        return (
            DatabaseConnection().client
            .table("person")
            .select("*")
            .eq("person_id", person_id)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("person").insert(data).execute().data

    @staticmethod
    def update(person_id, data):
        return (
            DatabaseConnection().client
            .table("person")
            .update(data)
            .eq("person_id", person_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(person_id):
        return (
            DatabaseConnection().client
            .table("person")
            .delete()
            .eq("person_id", person_id)
            .execute()
            .data
        )
