import unittest
from types import SimpleNamespace
from unittest.mock import patch

try:
    import backend.app.services.lesson as lesson_svc
except ModuleNotFoundError:
    import app.services.lesson as lesson_svc


class _FakeQuery:
    def __init__(self, rows):
        self._rows = list(rows)

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self._rows = [row for row in self._rows if row.get(key) == value]
        return self

    def execute(self):
        return SimpleNamespace(data=self._rows)


class _FakeClient:
    def __init__(self, table_rows):
        self._table_rows = table_rows

    def table(self, name):
        return _FakeQuery(self._table_rows.get(name, []))


class LessonValidationTests(unittest.TestCase):
    def _base_payload(self):
        return {
            "lesson_id": 200,
            "instructor_id": 1,
            "student_id": 3,
            "room_id": 2,
            "instrument": "Piano",
            "start_time": "2026-03-25T10:30:00",
            "end_time": "2026-03-25T11:30:00",
        }

    def _base_tables(self):
        return {
            "lesson": [],
            "instructor": [{"instructor_id": 1, "name": "Instructor One"}],
            "instructor_skill": [{"instructor_id": 1, "skill": "Piano", "min_skill_level": 2}],
            "student_skill": [{"student_id": 3, "skill": "Piano", "skill_level": 3}],
        }

    def test_validate_rejects_room_double_booking(self):
        payload = self._base_payload()
        tables = self._base_tables()
        tables["lesson"] = [
            {
                "lesson_id": 99,
                "instructor_id": 9,
                "student_id": 8,
                "room_id": 2,
                "room_name": "Studio A",
                "start_time": "2026-03-25T10:00:00",
                "end_time": "2026-03-25T11:00:00",
            }
        ]

        with patch.object(lesson_svc, "_db", return_value=_FakeClient(tables)):
            is_valid, message = lesson_svc.validate_lesson_overlaps(payload)

        self.assertFalse(is_valid)
        self.assertIn("Studio A is already booked 10:00", message)

    def test_validate_rejects_instructor_double_booking(self):
        payload = self._base_payload()
        tables = self._base_tables()
        tables["lesson"] = [
            {
                "lesson_id": 101,
                "instructor_id": 1,
                "instructor_name": "Instructor One",
                "student_id": 11,
                "room_id": 12,
                "start_time": "2026-03-25T10:00:00",
                "end_time": "2026-03-25T11:00:00",
            }
        ]

        with patch.object(lesson_svc, "_db", return_value=_FakeClient(tables)):
            is_valid, message = lesson_svc.validate_lesson_overlaps(payload)

        self.assertFalse(is_valid)
        self.assertIn("Instructor One is already teaching 10:00", message)

    def test_validate_rejects_student_double_booking(self):
        payload = self._base_payload()
        tables = self._base_tables()
        tables["lesson"] = [
            {
                "lesson_id": 102,
                "instructor_id": 19,
                "student_id": 3,
                "student_name": "Student Three",
                "room_id": 20,
                "start_time": "2026-03-25T10:00:00",
                "end_time": "2026-03-25T11:00:00",
            }
        ]

        with patch.object(lesson_svc, "_db", return_value=_FakeClient(tables)):
            is_valid, message = lesson_svc.validate_lesson_overlaps(payload)

        self.assertFalse(is_valid)
        self.assertIn("Student Three already has a lesson 10:00", message)

    def test_validate_rejects_instrument_mismatch(self):
        payload = self._base_payload()
        payload["instrument"] = "Violin"
        tables = self._base_tables()

        with patch.object(lesson_svc, "_db", return_value=_FakeClient(tables)):
            is_valid, message = lesson_svc.validate_lesson_overlaps(payload)

        self.assertFalse(is_valid)
        self.assertEqual("Instructor One is not certified to teach Violin", message)

    def test_validate_rejects_skill_level_mismatch(self):
        payload = self._base_payload()
        tables = self._base_tables()
        tables["instructor_skill"] = [{"instructor_id": 1, "skill": "Piano", "min_skill_level": 5}]
        tables["student_skill"] = [{"student_id": 3, "skill": "Piano", "skill_level": 2}]

        with patch.object(lesson_svc, "_db", return_value=_FakeClient(tables)):
            is_valid, message = lesson_svc.validate_lesson_overlaps(payload)

        self.assertFalse(is_valid)
        self.assertEqual(
            "Skill level mismatch for Piano: instructor minimum is 5, student level is 2",
            message,
        )


if __name__ == "__main__":
    unittest.main()
