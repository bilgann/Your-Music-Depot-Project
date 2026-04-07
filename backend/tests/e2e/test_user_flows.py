# Tests have been split into separate files. See:
#
#   test_login.py              -- Flow 1:  Login / Authentication
#   test_dashboard.py          -- Flow 2:  Dashboard Home
#   test_sidebar.py            -- Flow 3:  Sidebar Navigation
#   test_logout.py             -- Flow 4:  Logout
#   test_schedule.py           -- Flow 5:  Schedule Page (Calendar)
#   test_add_lesson_modal.py   -- Flow 6:  Add Lesson Modal
#   test_edit_mode.py          -- Flow 7:  Edit Mode (lesson edit / delete buttons)
#   test_token_persistence.py  -- Flow 8:  Token Persistence (page refresh)
#   test_clients_page.py       -- Flow 9:  Clients Management (CRUD, search, pagination)
#   test_client_detail.py      -- Flow 10: Client Detail (tabs, actions, breadcrumb)
#   test_students_page.py      -- Flow 11: Students Management (CRUD, search, pagination)
#   test_student_detail.py     -- Flow 12: Student Detail (tabs, breadcrumb)
#   test_instructors_page.py   -- Flow 13: Instructors Management (CRUD, search)
#   test_rooms_page.py         -- Flow 14: Rooms Management (CRUD, search, pagination)
#   test_payments_page.py      -- Flow 15: Payments Management (record, delete)
#   test_settings_page.py      -- Flow 16: Settings (user info from JWT)
#   test_auth_guard.py         -- Flow 17: Auth Guards (protected route redirects)
#
# Shared config, driver factory, and base class are in base.py.
#
# Run all e2e tests:
#   $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/ -v
