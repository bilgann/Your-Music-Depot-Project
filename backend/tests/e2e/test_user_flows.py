# Tests have been split into separate files. See:
#
#   test_login.py             – Flow 1: Login / Authentication
#   test_dashboard.py         – Flow 2: Dashboard Home
#   test_sidebar.py           – Flow 3: Sidebar Navigation
#   test_logout.py            – Flow 4: Logout
#   test_schedule.py          – Flow 5: Schedule Page (Calendar)
#   test_add_lesson_modal.py  – Flow 6: Add Lesson Modal
#   test_edit_mode.py         – Flow 7: Edit Mode (lesson edit / delete buttons)
#   test_token_persistence.py – Flow 8: Token Persistence (page refresh)
#
# Shared config, driver factory, and base class are in base.py.
#
# Run all e2e tests:
#   $env:PYTHONPATH="."; python -m pytest backend/tests/e2e/ -v
