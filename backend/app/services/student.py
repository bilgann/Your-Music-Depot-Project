from backend.app.models.student import Student


def get_all_students():
    return Student.get_all()


def get_student_by_id(student_id):
    return Student.get(student_id)


def create_student(data):
    return Student.create(data)


def update_student(student_id, data):
    return Student.update(student_id, data)


def delete_student(student_id):
    return Student.delete(student_id)
