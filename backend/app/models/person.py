from backend.app.singletons.database import DatabaseConnection


class Person:
    def __init__(self, person_id, name, email=None, phone=None):
        self.person_id = person_id
        self.name = name
        self.email = email
        self.phone = phone

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
