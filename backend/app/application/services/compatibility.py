from backend.app.domain.entities.credential import CredentialEntity
from backend.app.domain.entities.instructor import InstructorEntity
from backend.app.domain.entities.instructor_student_compatibility import InstructorStudentCompatibilityEntity
from backend.app.domain.entities.student import StudentEntity
from backend.app.domain.exceptions.exceptions import NotFoundError
from backend.app.domain.services import compatibility_service
from backend.app.infrastructure.database.repositories import (
    Credential,
    Instructor,
    InstructorStudentCompatibility,
    Student,
)


def check_compatibility(student_id: str, instructor_id: str) -> dict:
    """
    Run all three compatibility layers and return a result dict.
    Raises NotFoundError if either party doesn't exist.
    """
    srows = Student.get(student_id)
    if not srows:
        raise NotFoundError("Student not found.")
    irows = Instructor.get(instructor_id)
    if not irows:
        raise NotFoundError("Instructor not found.")

    student    = StudentEntity.from_dict(srows[0])
    instructor = InstructorEntity.from_dict(irows[0])
    credentials = [
        CredentialEntity.from_dict(r)
        for r in Credential.get_by_instructor(instructor_id)
    ]
    pair_overrides = [
        InstructorStudentCompatibilityEntity.from_dict(r)
        for r in InstructorStudentCompatibility.get(instructor_id, student_id)
    ]

    result = compatibility_service.check(student, instructor, credentials, pair_overrides)
    return {
        "can_assign":   result.can_assign,
        "hard_verdict": result.hard_verdict,
        "soft_verdict": result.soft_verdict,
        "reasons":      list(result.reasons),
    }


def filter_compatible_instructors(student_id: str) -> list:
    """
    Return all instructors compatible with the given student, sorted by verdict
    (required → preferred → neutral → disliked).
    """
    srows = Student.get(student_id)
    if not srows:
        raise NotFoundError("Student not found.")
    student = StudentEntity.from_dict(srows[0])

    instructors = [InstructorEntity.from_dict(r) for r in Instructor.get_all()]
    all_credentials = [CredentialEntity.from_dict(r) for r in Credential.get_all()]
    all_overrides = [
        InstructorStudentCompatibilityEntity.from_dict(r)
        for r in InstructorStudentCompatibility.get_by_student(student_id)
    ]

    ranked = compatibility_service.filter_compatible(
        student, instructors, all_credentials, all_overrides
    )
    return [
        {
            "instructor_id": instr.instructor_id,
            "hard_verdict":  result.hard_verdict,
            "soft_verdict":  result.soft_verdict,
            "reasons":       list(result.reasons),
        }
        for instr, result in ranked
    ]


def filter_compatible_students(instructor_id: str) -> list:
    """
    Return all students compatible with the given instructor.
    """
    irows = Instructor.get(instructor_id)
    if not irows:
        raise NotFoundError("Instructor not found.")
    instructor = InstructorEntity.from_dict(irows[0])

    credentials = [CredentialEntity.from_dict(r) for r in Credential.get_by_instructor(instructor_id)]
    all_overrides = [
        InstructorStudentCompatibilityEntity.from_dict(r)
        for r in InstructorStudentCompatibility.get_by_instructor(instructor_id)
    ]

    compatible = []
    for srow in Student.get_all():
        student = StudentEntity.from_dict(srow)
        result = compatibility_service.check(student, instructor, credentials, all_overrides)
        if result.can_assign:
            compatible.append({
                "student_id":   student.student_id,
                "hard_verdict": result.hard_verdict,
                "soft_verdict": result.soft_verdict,
                "reasons":      list(result.reasons),
            })
    return compatible


def set_compatibility(data: dict) -> dict:
    """Create or update a compatibility override between an instructor and student."""
    existing = InstructorStudentCompatibility.get(
        data["instructor_id"], data["student_id"]
    )
    if existing:
        return InstructorStudentCompatibility.update(
            existing[0]["compatibility_id"], data
        )
    return InstructorStudentCompatibility.create(data)


def delete_compatibility(compatibility_id: str):
    return InstructorStudentCompatibility.delete(compatibility_id)
