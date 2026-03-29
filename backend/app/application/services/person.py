from backend.app.infrastructure.models import Person


def get_all_persons():
    return Person.get_all()


def get_person_by_id(person_id):
    return Person.get(person_id)


def create_person(data):
    return Person.create(data)


def update_person(person_id, data):
    return Person.update(person_id, data)


def delete_person(person_id):
    return Person.delete(person_id)
