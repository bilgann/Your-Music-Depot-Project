# Setup Guide — Your Music Depot
# Skip step 2 & 3 if prof, mabye do step 3c 
## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11+ | |
| Node.js | 20+ | |
| npm | 10+ | Bundled with Node |
| Git | any | |

You also need a [Supabase](https://supabase.com) account (free tier is fine).

---

## 1. Clone the Repository

```bash
git clone <repo-url>
cd Your-Music-Depot-Project
git checkout dev
```

---

## 2. Supabase Project

1. Go to [supabase.com](https://supabase.com) → **New project**.
2. Note your **Project URL** and **anon/service role key** (Settings → API).
3. Open the **SQL Editor** and run the migrations **in order**:

```
supabase/migrations/20260329000000_initial_schema.sql
supabase/migrations/20260329000001_disable_rls.sql
supabase/migrations/20260329000002_school_schedule.sql
supabase/migrations/20260409000000_lesson_capacity.sql
supabase/migrations/20260409000001_student_blocked_times.sql
```

Copy-paste each file's contents into the SQL Editor and click **Run**.

---

## 3. Backend

### 3a. Create the environment file

```bash
cp backend/example.env backend/.env
```

Edit `backend/.env` and fill in your Supabase credentials:

```
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_KEY=<your-anon-or-service-role-key>
```

The E2E fields are only needed for Selenium tests — leave them blank for now.

### 3b. Install Python dependencies

```bash
# From the project root
pip install -r backend/requirements.txt
```

Using a virtual environment is recommended:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3c. Seed the database

```bash
python backend/seed.py
```

This inserts ~5 years of realistic data (20 instructors, 500 students, ~11 500 lesson occurrences, ~6 000 invoices).

To wipe and re-seed from scratch:

```bash
python backend/seed.py --clear
```

Default login credentials created by the seed:

| Username | Password |
|----------|----------|
| `admin`  | `password` |
| `barnes` | `password` |

### 3d. Start the Flask API

```bash
python backend/app.py
```

The API runs at `http://localhost:5000` by default.

---

## 4. Frontend

### 4a. Install dependencies

```bash
cd frontend
npm install
```

### 4b. Start the dev server

```bash
npm run dev
```

The app runs at `http://localhost:3000`.

---

## 5. Running Tests

### Unit tests (Python)

```bash
# From the project root
python -m pytest backend/tests/unit
```

### Integration tests (Python)

```bash
python -m pytest backend/tests/integration
```

### Frontend tests

```bash
cd frontend
npm test
```

### E2E tests (Selenium)

#### Prerequisites

**Google Chrome** must be installed. ChromeDriver is managed automatically by `webdriver-manager` (already in `requirements.txt`) — it downloads a matching driver on first run.

#### Environment variables

Add these to `backend/.env`:

```
E2E_BASE_URL=http://localhost:3000
E2E_USERNAME=barnes
E2E_PASSWORD=password
E2E_HEADLESS=1
```

| Variable | Default | Notes |
|----------|---------|-------|
| `E2E_BASE_URL` | `http://localhost:3000` | URL of the running Next.js app |
| `E2E_USERNAME` | `barnes` | Must exist in the seeded DB |
| `E2E_PASSWORD` | `password` | |
| `E2E_HEADLESS` | `0` | Set to `1` to run without opening a browser window |
| `E2E_DISPLAY_X` | `1920` | X position of the browser window (useful for dual-monitor setups) |
| `E2E_DISPLAY_Y` | `0` | Y position of the browser window |

#### Run the suite

Both servers must be running before you start:

```bash
# Terminal 1 — Flask API
python backend/app.py

# Terminal 2 — Next.js
cd frontend && npm run dev

# Terminal 3 — E2E tests
python -m pytest backend/tests/e2e
```

Run a single test file:

```bash
python -m pytest backend/tests/e2e/test_login.py
```

Run a single test method:

```bash
python -m pytest backend/tests/e2e/test_login.py::LoginTest::test_valid_login
```

#### How the suite works

- One Chrome window is shared across all test methods within a class (opened in `setUpClass`, closed in `tearDownClass`).
- Before each test, `setUp` navigates to `/home` and re-authenticates automatically if the session was lost.
- Test classes that need an unauthenticated browser (e.g. login-page tests) call `self._clear_session()` instead.

#### Troubleshooting

| Problem | Fix |
|---------|-----|
| `WebDriverException: Chrome not reachable` | Install Google Chrome |
| `SessionNotCreatedException: Chrome version mismatch` | `pip install --upgrade webdriver-manager` |
| Tests time out on CI / slow machine | Increase `DEFAULT_TIMEOUT` in `backend/tests/e2e/base.py` (default: 10 s) |
| Window opens on wrong monitor | Set `E2E_DISPLAY_X` / `E2E_DISPLAY_Y` in `.env` |

---

## Quick-start Checklist

- [ ] Supabase project created and migrations applied
- [ ] `backend/.env` filled in with `SUPABASE_URL` and `SUPABASE_KEY`
- [ ] Python dependencies installed
- [ ] Database seeded (`python backend/seed.py`)
- [ ] Flask API running (`python backend/app.py`)
- [ ] Frontend dependencies installed (`npm install` in `frontend/`)
- [ ] Next.js dev server running (`npm run dev` in `frontend/`)
- [ ] Login at `http://localhost:3000` with `admin` / `password`
- [ ] most of this is claude code with human guidance
