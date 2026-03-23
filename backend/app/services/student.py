from backend.app.singletons.database import DatabaseConnection


def _db():
    return DatabaseConnection().client


def get_all_students():
    return _db().table("student").select("*").execute().data


def get_student_by_id(student_id):
    return _db().table("student").select("*").eq("student_id", student_id).execute().data


def create_student(data):
    return _db().table("student").insert(data).execute().data


def update_student(student_id, data):
    return _db().table("student").update(data).eq("student_id", student_id).execute().data


def delete_student(student_id):
    return _db().table("student").delete().eq("student_id", student_id).execute().data