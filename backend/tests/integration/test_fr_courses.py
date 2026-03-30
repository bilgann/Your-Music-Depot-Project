"""
Integration tests covering course management endpoints:

  FR-04 — Course CRUD: create, read, update, delete courses
  FR-09 — Roster management: enroll/unenroll students, add/remove instructors
  FR-10 — Schedule projection: POST /api/courses/<id>/project

All endpoints require authentication; admin endpoints require the admin role.
"""
import unittest
from unittest.mock import MagicMock, patch

from backend.app.application.singletons import Auth
from backend.app.infrastructure.database.database import DatabaseConnection


# ── App + auth setup ──────────────────────────────────────────────────────────

def _build():
    DatabaseConnection._instance = MagicMock()
    Auth._instance = None
    from backend import build_app
    app = build_app()
    app.config["TESTING"] = True
    return app.test_client()


_client = _build()
_login_res = _client.post("/user/login?username=barnes&password=password")
_H = {"Authorization": f"Bearer {_login_res.get_json()['data']}"}

_SVC = "backend.app.application.services.course"
_AUDIT = "backend.app.application.services.audit.log"

_VALID_COURSE = {
    "name": "Beginner Guitar – Spring 2025",
    "room_id": "r1",
    "instructor_ids": ["i1"],
    "student_ids": [],
    "period_start": "2025-09-01",
    "period_end": "2025-12-31",
    "recurrence": "0 10 * * MON",
    "start_time": "10:00:00",
    "end_time": "11:00:00",
    "status": "draft",
}

_COURSE_ROW = {
    "course_id": "c1",
    **_VALID_COURSE,
}


# ── GET /api/courses ──────────────────────────────────────────────────────────

class TestListCourses(unittest.TestCase):

    def test_list_courses_returns_200_for_authenticated(self):
        with patch(f"{_SVC}.get_all_courses", return_value=[]):
            res = _client.get("/api/courses", headers=_H)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    def test_list_courses_requires_auth(self):
        with patch(f"{_SVC}.get_all_courses", return_value=[]):
            res = _client.get("/api/courses")
        self.assertEqual(res.status_code, 401)

    def test_list_courses_by_instructor_filter(self):
        data = [_COURSE_ROW]
        with patch(f"{_SVC}.get_courses_by_instructor", return_value=data) as mock_svc:
            res = _client.get("/api/courses?instructor_id=i1", headers=_H)
        self.assertEqual(res.status_code, 200)
        mock_svc.assert_called_once_with("i1")

    def test_list_courses_by_student_filter(self):
        data = [_COURSE_ROW]
        with patch(f"{_SVC}.get_courses_by_student", return_value=data) as mock_svc:
            res = _client.get("/api/courses?student_id=s1", headers=_H)
        self.assertEqual(res.status_code, 200)
        mock_svc.assert_called_once_with("s1")

    def test_list_courses_returns_data_array(self):
        data = [_COURSE_ROW, {**_COURSE_ROW, "course_id": "c2", "name": "Course 2"}]
        with patch(f"{_SVC}.get_all_courses", return_value=data):
            res = _client.get("/api/courses", headers=_H)
        self.assertEqual(len(res.get_json()["data"]), 2)


# ── GET /api/courses/<id> ─────────────────────────────────────────────────────

class TestGetCourse(unittest.TestCase):

    def test_get_course_returns_200(self):
        with patch(f"{_SVC}.get_course_by_id", return_value=[_COURSE_ROW]):
            res = _client.get("/api/courses/c1", headers=_H)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    def test_get_course_not_found_returns_404(self):
        with patch(f"{_SVC}.get_course_by_id", return_value=[]):
            res = _client.get("/api/courses/nobody", headers=_H)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(res.get_json()["success"])

    def test_get_course_returns_single_object(self):
        with patch(f"{_SVC}.get_course_by_id", return_value=[_COURSE_ROW]):
            res = _client.get("/api/courses/c1", headers=_H)
        data = res.get_json()["data"]
        self.assertEqual(data["course_id"], "c1")

    def test_get_course_requires_auth(self):
        with patch(f"{_SVC}.get_course_by_id", return_value=[_COURSE_ROW]):
            res = _client.get("/api/courses/c1")
        self.assertEqual(res.status_code, 401)


# ── POST /api/courses ─────────────────────────────────────────────────────────

class TestCreateCourse(unittest.TestCase):

    def test_create_course_returns_201(self):
        with patch(f"{_SVC}.create_course", return_value=[_COURSE_ROW]), \
             patch(_AUDIT):
            res = _client.post("/api/courses", json=_VALID_COURSE, headers=_H)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()["success"])

    def test_create_course_missing_name_returns_422(self):
        payload = {k: v for k, v in _VALID_COURSE.items() if k != "name"}
        res = _client.post("/api/courses", json=payload, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_create_course_requires_auth(self):
        with patch(f"{_SVC}.create_course", return_value=[_COURSE_ROW]):
            res = _client.post("/api/courses", json=_VALID_COURSE)
        self.assertEqual(res.status_code, 401)

    def test_create_course_empty_body_returns_422(self):
        res = _client.post("/api/courses", json={}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_create_course_with_fk_violation_returns_409(self):
        from backend.app.domain.exceptions.exceptions import ConflictError
        with patch(f"{_SVC}.create_course",
                   side_effect=Exception("ERROR: 23503 foreign key violation")):
            res = _client.post("/api/courses", json=_VALID_COURSE, headers=_H)
        self.assertEqual(res.status_code, 409)


# ── PUT /api/courses/<id> ─────────────────────────────────────────────────────

class TestUpdateCourse(unittest.TestCase):

    def test_update_course_returns_200(self):
        with patch(f"{_SVC}.update_course", return_value=[_COURSE_ROW]), \
             patch(_AUDIT):
            res = _client.put("/api/courses/c1", json={"status": "active"}, headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_update_course_requires_auth(self):
        with patch(f"{_SVC}.update_course", return_value=[]):
            res = _client.put("/api/courses/c1", json={"status": "active"})
        self.assertEqual(res.status_code, 401)

    def test_update_course_type_mismatch_returns_422(self):
        """capacity must be an int, not a string."""
        res = _client.put("/api/courses/c1", json={"capacity": "big"}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_update_course_partial_does_not_require_all_fields(self):
        with patch(f"{_SVC}.update_course", return_value=[]), \
             patch(_AUDIT):
            res = _client.put("/api/courses/c1", json={"name": "New Name"}, headers=_H)
        self.assertEqual(res.status_code, 200)


# ── DELETE /api/courses/<id> ──────────────────────────────────────────────────

class TestDeleteCourse(unittest.TestCase):

    def test_delete_course_returns_200(self):
        with patch(f"{_SVC}.delete_course", return_value=None), \
             patch(_AUDIT):
            res = _client.delete("/api/courses/c1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_delete_course_requires_auth(self):
        with patch(f"{_SVC}.delete_course", return_value=None):
            res = _client.delete("/api/courses/c1")
        self.assertEqual(res.status_code, 401)

    def test_delete_course_with_fk_violation_returns_409(self):
        with patch(f"{_SVC}.delete_course",
                   side_effect=Exception("ERROR: 23503 foreign key violation")):
            res = _client.delete("/api/courses/c1", headers=_H)
        self.assertEqual(res.status_code, 409)


# ── POST /api/courses/<id>/students ───────────────────────────────────────────

class TestEnrollStudent(unittest.TestCase):

    def test_enroll_student_returns_201(self):
        with patch(f"{_SVC}.enroll_student", return_value=[_COURSE_ROW]), \
             patch(_AUDIT):
            res = _client.post("/api/courses/c1/students",
                               json={"student_id": "s1"}, headers=_H)
        self.assertEqual(res.status_code, 201)

    def test_enroll_student_missing_student_id_returns_422(self):
        res = _client.post("/api/courses/c1/students", json={}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_enroll_student_requires_auth(self):
        with patch(f"{_SVC}.enroll_student", return_value=[]):
            res = _client.post("/api/courses/c1/students", json={"student_id": "s1"})
        self.assertEqual(res.status_code, 401)

    def test_enroll_duplicate_student_returns_conflict(self):
        with patch(f"{_SVC}.enroll_student",
                   side_effect=Exception("ERROR: 23505 unique constraint")):
            res = _client.post("/api/courses/c1/students",
                               json={"student_id": "s1"}, headers=_H)
        self.assertEqual(res.status_code, 409)


# ── DELETE /api/courses/<id>/students/<student_id> ────────────────────────────

class TestUnenrollStudent(unittest.TestCase):

    def test_unenroll_student_returns_200(self):
        with patch(f"{_SVC}.unenroll_student", return_value=[]), \
             patch(_AUDIT):
            res = _client.delete("/api/courses/c1/students/s1", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_unenroll_student_requires_auth(self):
        with patch(f"{_SVC}.unenroll_student", return_value=[]):
            res = _client.delete("/api/courses/c1/students/s1")
        self.assertEqual(res.status_code, 401)


# ── POST /api/courses/<id>/instructors ────────────────────────────────────────

class TestAddInstructor(unittest.TestCase):

    def test_add_instructor_returns_200(self):
        with patch(f"{_SVC}.add_instructor", return_value=[_COURSE_ROW]), \
             patch(_AUDIT):
            res = _client.post("/api/courses/c1/instructors",
                               json={"instructor_id": "i2"}, headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_add_instructor_missing_instructor_id_returns_422(self):
        res = _client.post("/api/courses/c1/instructors", json={}, headers=_H)
        self.assertEqual(res.status_code, 422)

    def test_add_instructor_requires_auth(self):
        with patch(f"{_SVC}.add_instructor", return_value=[]):
            res = _client.post("/api/courses/c1/instructors",
                               json={"instructor_id": "i2"})
        self.assertEqual(res.status_code, 401)


# ── DELETE /api/courses/<id>/instructors/<instructor_id> ──────────────────────

class TestRemoveInstructor(unittest.TestCase):

    def test_remove_instructor_returns_200(self):
        with patch(f"{_SVC}.remove_instructor", return_value=[_COURSE_ROW]), \
             patch(_AUDIT):
            res = _client.delete("/api/courses/c1/instructors/i2", headers=_H)
        self.assertEqual(res.status_code, 200)

    def test_remove_last_instructor_returns_409(self):
        from backend.app.domain.exceptions.exceptions import ConflictError
        with patch(f"{_SVC}.remove_instructor",
                   side_effect=ConflictError("Cannot remove the last instructor.")):
            res = _client.delete("/api/courses/c1/instructors/i1", headers=_H)
        self.assertEqual(res.status_code, 409)

    def test_remove_instructor_requires_auth(self):
        with patch(f"{_SVC}.remove_instructor", return_value=[]):
            res = _client.delete("/api/courses/c1/instructors/i1")
        self.assertEqual(res.status_code, 401)


# ── POST /api/courses/<id>/project ────────────────────────────────────────────

class TestProjectCourseSchedule(unittest.TestCase):

    def test_project_returns_201(self):
        with patch(f"{_SVC}.project_course_schedule", return_value=[{"occurrence_id": "o1"}]), \
             patch(_AUDIT):
            res = _client.post("/api/courses/c1/project", headers=_H)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()["success"])

    def test_project_returns_occurrence_count_in_message(self):
        occurrences = [{"occurrence_id": f"o{i}"} for i in range(4)]
        with patch(f"{_SVC}.project_course_schedule", return_value=occurrences), \
             patch(_AUDIT):
            res = _client.post("/api/courses/c1/project", headers=_H)
        body = res.get_json()
        self.assertIn("4", body["message"])

    def test_project_requires_auth(self):
        with patch(f"{_SVC}.project_course_schedule", return_value=[]):
            res = _client.post("/api/courses/c1/project")
        self.assertEqual(res.status_code, 401)

    def test_project_course_not_found_returns_404(self):
        from backend.app.domain.exceptions.exceptions import NotFoundError
        with patch(f"{_SVC}.project_course_schedule",
                   side_effect=NotFoundError("Course not found.")):
            res = _client.post("/api/courses/c1/project", headers=_H)
        self.assertEqual(res.status_code, 404)

    def test_project_empty_course_returns_zero_occurrences(self):
        with patch(f"{_SVC}.project_course_schedule", return_value=[]), \
             patch(_AUDIT):
            res = _client.post("/api/courses/c1/project", headers=_H)
        body = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertIn("0", body["message"])


# ── Response structure ────────────────────────────────────────────────────────

class TestCourseResponseStructure(unittest.TestCase):
    """All course responses must follow the standard ResponseContract shape."""

    def test_success_response_has_success_true(self):
        with patch(f"{_SVC}.get_all_courses", return_value=[]):
            res = _client.get("/api/courses", headers=_H)
        self.assertIn("success", res.get_json())
        self.assertTrue(res.get_json()["success"])

    def test_error_response_has_success_false(self):
        with patch(f"{_SVC}.get_course_by_id", return_value=[]):
            res = _client.get("/api/courses/nobody", headers=_H)
        self.assertFalse(res.get_json()["success"])

    def test_success_response_has_message(self):
        with patch(f"{_SVC}.get_all_courses", return_value=[]):
            res = _client.get("/api/courses", headers=_H)
        self.assertIn("message", res.get_json())


if __name__ == "__main__":
    unittest.main()
