from backend.app.singletons.database import DatabaseConnection


def _db():
    return DatabaseConnection().client


def get_all_instructors():
    return _db().table("instructor").select("*").execute().data


def get_instructor_by_id(instructor_id):
    return _db().table("instructor").select("*").eq("instructor_id", instructor_id).execute().data


def create_instructor(data):
    return _db().table("instructor").insert(data).execute().data


def update_instructor(instructor_id, data):
    return _db().table("instructor").update(data).eq("instructor_id", instructor_id).execute().data


def delete_instructor(instructor_id):
    return _db().table("instructor").delete().eq("instructor_id", instructor_id).execute().data