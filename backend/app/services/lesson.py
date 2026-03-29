from backend.app.models.lesson import Lesson


def get_all_lessons():
    return Lesson.get_all()


def get_lessons_for_week(start, end):
    return Lesson.get_for_week(start, end)


def get_lesson_by_id(lesson_id):
    return Lesson.get(lesson_id)


def create_lesson(data):
    return Lesson.create(data)


def update_lesson(lesson_id, data):
    return Lesson.update(lesson_id, data)


def delete_lesson(lesson_id):
    return Lesson.delete(lesson_id)
