from backend.app.domain.exceptions.exceptions import NotFoundError
from backend.app.infrastructure.database.repositories import Credential, Instructor


def get_all_credentials():
    return Credential.get_all()


def get_credential_by_id(credential_id):
    return Credential.get(credential_id)


def get_credentials_by_instructor(instructor_id):
    return Credential.get_by_instructor(instructor_id)


def get_active_credentials_by_instructor(instructor_id):
    return Credential.get_active_by_instructor(instructor_id)


def create_credential(data):
    instructor_id = data.get("instructor_id")
    if instructor_id and not Instructor.get(instructor_id):
        raise NotFoundError(f"Instructor {instructor_id} not found.")
    return Credential.create(data)


def update_credential(credential_id, data):
    if not Credential.get(credential_id):
        raise NotFoundError("Credential not found.")
    return Credential.update(credential_id, data)


def delete_credential(credential_id):
    if not Credential.get(credential_id):
        raise NotFoundError("Credential not found.")
    return Credential.delete(credential_id)
