from backend.app.models.instructor import Instructor


def get_all_instructors():
    return Instructor.get_all()


def list_instructors(page: int = 1, page_size: int = 20, search: str = None):
    return Instructor.list(page, page_size, search)


def get_instructor_by_id(instructor_id):
    return Instructor.get(instructor_id)


def create_instructor(data):
    return Instructor.create(data)


def update_instructor(instructor_id, data):
    return Instructor.update(instructor_id, data)


def delete_instructor(instructor_id):
    return Instructor.delete(instructor_id)
