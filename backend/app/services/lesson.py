from backend.app.singletons.database import DatabaseConnection


def _db():
    return DatabaseConnection().client


def get_all_lessons():
    return _db().table("lesson").select("*").execute().data


def get_lessons_for_week(start, end):
    return _db().table("lesson").select("*").gte("start_time", start).lte("end_time", end).execute().data


def get_lesson_by_id(lesson_id):
    return _db().table("lesson").select("*").eq("lesson_id", lesson_id).execute().data


def create_lesson(data):
    return _db().table("lesson").insert(data).execute().data


def update_lesson(lesson_id, data):
    return _db().table("lesson").update(data).eq("lesson_id", lesson_id).execute().data


def delete_lesson(lesson_id):
    return _db().table("lesson").delete().eq("lesson_id", lesson_id).execute().data