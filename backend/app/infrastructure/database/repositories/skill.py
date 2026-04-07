from backend.app.infrastructure.database.database import DatabaseConnection

# Domain entity: backend.app.domain.entities.SkillEntity


class Skill:
    @staticmethod
    def get_all():
        return DatabaseConnection().client.table("skill").select("*").execute().data

    @staticmethod
    def get(skill_id):
        return (
            DatabaseConnection().client
            .table("skill")
            .select("*")
            .eq("skill_id", skill_id)
            .execute()
            .data
        )

    @staticmethod
    def create(data):
        return DatabaseConnection().client.table("skill").insert(data).execute().data

    @staticmethod
    def update(skill_id, data):
        return (
            DatabaseConnection().client
            .table("skill")
            .update(data)
            .eq("skill_id", skill_id)
            .execute()
            .data
        )

    @staticmethod
    def delete(skill_id):
        return (
            DatabaseConnection().client
            .table("skill")
            .delete()
            .eq("skill_id", skill_id)
            .execute()
            .data
        )
