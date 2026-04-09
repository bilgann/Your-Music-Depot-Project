# Running the Tests

All commands are run from the **project root** (`Your-Music-Depot-Project/`).

> **Windows note:** Use `$env:PYTHONPATH="."` in PowerShell to set the path, or prefix commands as shown below.

---

## Backend — Unit Tests

No servers needed. Tests run in isolation.

```powershell
$env:PYTHONPATH="."; python -m pytest backend/tests/unit/ -v
```

---

## Backend — Integration Tests

No servers needed. These mock the database and auth singletons internally.

```powershell
$env:PYTHONPATH="."; python -m pytest backend/tests/integration/ -v
```

---

## Backend — E2E Tests (Selenium)

**Prerequisites:**
- Both servers must be running (backend on `:5000`, frontend on `:3000`)
- Google Chrome installed
- `webdriver-manager` handles chromedriver automatically (already in `requirements.txt`)

**Start servers first:**
```powershell
# Terminal 1
$env:PYTHONPATH="."; python backend/app.py

# Terminal 2
cd frontend; npm run dev
```

**Run all e2e tests:**
```powershell
$env:PYTHONPATH="."; python -m pytest backend/tests/e2e/ -v
```

**Run a specific flow:**
```powershell
$env:PYTHONPATH="."; python -m pytest backend/tests/e2e/test_login.py -v
```

| File | Flow |
|---|---|
| `test_login.py` | Login / Authentication |
| `test_dashboard.py` | Dashboard Home |
| `test_sidebar.py` | Sidebar Navigation |
| `test_logout.py` | Logout |
| `test_schedule.py` | Schedule Page (Calendar) |
| `test_add_lesson_modal.py` | Add Lesson Modal |
| `test_edit_mode.py` | Edit Mode (lesson edit / delete) |
| `test_token_persistence.py` | Token Persistence (page refresh) |
| `test_schedule_conflicts.py` | Schedule Conflicts (add lessons, instructor/room/capacity conflicts) |
| `test_student_timetable.py` | Student Timetable (generate schedule, week/month views, navigation) |

**Optional env vars** (set before running):
```powershell
$env:PYTHONPATH="."; $env:E2E_BASE_URL="http://localhost:3001"; $env:E2E_USERNAME="barnes"; $env:E2E_PASSWORD="password"; $env:E2E_HEADLESS="1"; python -m pytest backend/tests/e2e/ -v
```

> Note: The e2e tests default to `http://localhost:3000`. If your frontend is on `3001`, set `E2E_BASE_URL` as shown above.

---

## Frontend — Unit Tests

```powershell
cd frontend
npm test
```

Or in watch mode:
```powershell
npm run test:watch
```

---

## Run All Backend Tests at Once (excluding E2E)

```powershell
$env:PYTHONPATH="."; python -m pytest backend/tests/ -v --ignore=backend/tests/e2e
```
