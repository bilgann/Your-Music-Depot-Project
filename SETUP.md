# Your Music Depot — Setup Guide

This guide will get both the backend (server) and frontend (website) running on your computer. No technical experience needed — just follow each step in order.

---

## What You Will Need

Before starting, download and install these three programs. Each link goes to the official download page.

### 1. Python 3.12+
Python runs the backend server.

1. Go to https://www.python.org/downloads/
2. Click the big yellow **Download Python 3.12.x** button
3. Run the installer
4. **IMPORTANT:** On the first screen of the installer, tick the box that says **"Add Python to PATH"** before clicking Install

To check it worked, open **Command Prompt** (press `Win + R`, type `cmd`, press Enter) and type:
```
python --version
```
You should see something like `Python 3.12.x`.

---

### 2. Node.js 20 (LTS)
Node.js runs the frontend website.

1. Go to https://nodejs.org/
2. Click the **LTS** button (the one labelled "Recommended For Most Users")
3. Run the installer, click Next through all the steps

To check it worked, open Command Prompt and type:
```
node --version
```
You should see something like `v20.x.x`.

---

### 3. Git
Git is used to download the project code.

1. Go to https://git-scm.com/downloads
2. Click **Windows**, then download the installer
3. Run it, click Next through all the steps (the defaults are fine)

To check it worked, open Command Prompt and type:
```
git --version
```
You should see something like `git version 2.x.x`.

---

## Step 1 — Download the Project

Open Command Prompt and run these commands one at a time. Press Enter after each one.

```
cd %USERPROFILE%\Desktop
git clone <your-repository-url> YourMusicDepot
cd YourMusicDepot
```

Replace `<your-repository-url>` with the actual URL of the repository (e.g. from GitHub). After this, a folder called `YourMusicDepot` will appear on your Desktop.

---

## Step 2 — Create a Supabase Account and Project

Supabase is the database that stores all your data (students, lessons, payments, etc.). It is free to use.

1. Go to https://supabase.com and click **Start your project**
2. Sign up for a free account
3. Click **New project**
4. Fill in:
   - **Name:** YourMusicDepot (or anything you like)
   - **Database Password:** choose a strong password and **save it somewhere safe**
   - **Region:** pick the one closest to you
5. Click **Create new project** and wait about 1 minute for it to set up

---

## Step 3 — Create the Database Tables

Run the following SQL in the Supabase **SQL Editor** (left sidebar → SQL Editor → New query). Run each block separately.

### Core tables

```sql
-- User accounts
CREATE TABLE IF NOT EXISTS app_user (
    user_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    username  text UNIQUE NOT NULL,
    password  text NOT NULL,   -- SHA-256 hex digest
    role      text NOT NULL DEFAULT 'instructor' CHECK (role IN ('admin', 'instructor'))
);

-- Audit log (tracks all data changes)
CREATE TABLE IF NOT EXISTS audit_log (
    id          bigserial PRIMARY KEY,
    user_id     uuid,
    action      text NOT NULL CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'UPSERT')),
    entity_type text NOT NULL,
    entity_id   text,
    old_value   jsonb,
    new_value   jsonb,
    created_at  timestamptz NOT NULL DEFAULT now()
);
```

### Scheduling tables

```sql
-- Course: the top-level program aggregate (group classes or private lesson series)
CREATE TABLE IF NOT EXISTS course (
    course_id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name                 text NOT NULL,
    description          text,
    room_id              uuid REFERENCES room(room_id),
    instructor_ids       uuid[] NOT NULL DEFAULT '{}',
    student_ids          uuid[] NOT NULL DEFAULT '{}',
    period_start         date NOT NULL,
    period_end           date NOT NULL,
    recurrence           text NOT NULL,   -- cron expression or ISO date
    start_time           text NOT NULL,   -- HH:MM
    end_time             text NOT NULL,
    rate                 jsonb,           -- { charge_type, amount, currency }
    required_instruments jsonb NOT NULL DEFAULT '[]',
    capacity             int,
    skill_range          jsonb,           -- { min_level, max_level }
    status               text NOT NULL DEFAULT 'draft'
                             CHECK (status IN ('draft','active','completed','cancelled')),
    created_at           timestamptz NOT NULL DEFAULT now()
);

-- Lesson occurrence: a single materialised session (generated from lesson or course template)
CREATE TABLE IF NOT EXISTS lesson_occurrence (
    occurrence_id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id        uuid REFERENCES lesson(lesson_id),
    course_id        uuid REFERENCES course(course_id),
    date             date NOT NULL,
    start_time       text NOT NULL,
    end_time         text NOT NULL,
    instructor_id    uuid REFERENCES instructor(instructor_id),
    room_id          uuid REFERENCES room(room_id),
    status           text NOT NULL DEFAULT 'Scheduled',
    rate             jsonb,
    is_rescheduled   boolean NOT NULL DEFAULT false,
    cancelled_reason text,
    CONSTRAINT occurrence_has_source CHECK (
        (lesson_id IS NOT NULL) != (course_id IS NOT NULL)
        OR (lesson_id IS NOT NULL AND course_id IS NOT NULL)
    )
);
```

### Compatibility and credential tables

```sql
-- Instructor credentials (musical qualifications, CPR, special-ed certs, etc.)
CREATE TABLE IF NOT EXISTS credential (
    credential_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    instructor_id   uuid NOT NULL REFERENCES instructor(instructor_id),
    credential_type text NOT NULL DEFAULT 'musical',
    proficiencies   jsonb NOT NULL DEFAULT '[]',
    valid_from      date,
    valid_until     date,
    issued_by       text,
    issued_date     date
);

-- Per-pair instructor/student compatibility overrides
CREATE TABLE IF NOT EXISTS instructor_student_compatibility (
    compatibility_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    instructor_id    uuid NOT NULL REFERENCES instructor(instructor_id),
    student_id       uuid NOT NULL REFERENCES student(student_id),
    verdict          text NOT NULL CHECK (verdict IN ('blocked','disliked','preferred','required')),
    reason           text NOT NULL DEFAULT '',
    initiated_by     text NOT NULL CHECK (initiated_by IN ('student','instructor','admin')),
    created_at       timestamptz NOT NULL DEFAULT now()
);
```

### Update existing tables

```sql
-- lesson_enrollment now links to an occurrence, not a lesson directly
ALTER TABLE lesson_enrollment
    DROP COLUMN IF EXISTS lesson_id,
    ADD COLUMN IF NOT EXISTS occurrence_id uuid REFERENCES lesson_occurrence(occurrence_id);

-- lesson template gets student roster and optional course link
ALTER TABLE lesson
    ADD COLUMN IF NOT EXISTS student_ids uuid[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS course_id   uuid REFERENCES course(course_id);

-- student gets age (used for instructor age-restriction checks) and teaching requirements
ALTER TABLE student
    ADD COLUMN IF NOT EXISTS age          int,
    ADD COLUMN IF NOT EXISTS requirements jsonb NOT NULL DEFAULT '[]';

-- instructor gets teaching restrictions (min/max student age)
ALTER TABLE instructor
    ADD COLUMN IF NOT EXISTS restrictions jsonb NOT NULL DEFAULT '[]';

-- invoice_line gets item_type to support non-lesson charges
ALTER TABLE invoice_line
    ADD COLUMN IF NOT EXISTS item_type         text NOT NULL DEFAULT 'lesson',
    ADD COLUMN IF NOT EXISTS attendance_status text;

-- credit_transaction gets payment_method
ALTER TABLE credit_transaction
    ADD COLUMN IF NOT EXISTS payment_method text;
```

---

## Step 4 — Create Your First Admin User

You need to add yourself as an admin user. The password must be stored as a SHA-256 hash.

### Generate a password hash

Open Command Prompt and run:
```
python -c "import hashlib; print(hashlib.sha256('YourPasswordHere'.encode()).hexdigest())"
```

Replace `YourPasswordHere` with the password you want. Copy the long string printed — that is your hashed password.

### Insert the user into Supabase

In the Supabase **SQL Editor**, run:

```sql
INSERT INTO app_user (username, password, role)
VALUES ('your_username', 'paste_hash_here', 'admin');
```

---

## Step 5 — Get Your Supabase Keys

1. In your Supabase project, click **Project Settings** (gear icon) → **API**
2. You need:
   - **Project URL** — looks like `https://xxxxxxxxxxx.supabase.co`
   - **anon public** key — a long string starting with `eyJ...`

---

## Step 6 — Configure the Backend

1. Open the `backend` folder inside `YourMusicDepot`
2. Create a file called `.env` (the name starts with a dot, no other extension)
3. Open it with Notepad and paste the following, replacing values with your Supabase details:

```
SUPABASE_URL=https://xxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJyour_anon_key_here
JWT_SECRET=pick-any-long-random-string-here-at-least-32-characters
```

For `JWT_SECRET`, type any long random phrase — e.g. `my-music-depot-secret-key-2024-secure`.

Save the file.

---

## Step 7 — Start the Backend Server

Open Command Prompt and run:

```
cd %USERPROFILE%\Desktop\YourMusicDepot
python -m pip install -r backend\requirements.txt
python backend\app.py
```

The second command installs all required packages (only needed once). Key packages include:
- `flask`, `flask-cors` — web framework
- `supabase` — database client
- `python-dotenv` — loads `.env` files
- `PyJWT` — authentication tokens
- `croniter` — recurring schedule expansion (used for course and lesson projection)
- `selenium`, `webdriver-manager` — end-to-end testing only

You should see:
```
 * Running on http://127.0.0.1:5000
```

**Leave this Command Prompt window open** while using the app.

---

## Step 8 — Configure the Frontend

1. Open the `frontend` folder inside `YourMusicDepot`
2. Create a file called `.env.local`
3. Open it with Notepad and paste:

```
NEXT_PUBLIC_API_BASE=http://127.0.0.1:5000
```

Save the file.

---

## Step 9 — Start the Frontend

Open a **second** Command Prompt window and run:

```
cd %USERPROFILE%\Desktop\YourMusicDepot\frontend
npm install
npm run dev
```

You should see:
```
  ▲ Next.js
  - Local: http://localhost:3000
```

---

## Step 10 — Open the App

Open your browser and go to:
```
http://localhost:3000
```

Log in with the username and password you created in Step 4.

> **Temporary dev account:** Username `barnes`, password `password`. **Remove this before using the app with real data** — delete the fallback in `backend/app/infrastructure/database/repositories/user.py`.

---

## API Overview

The backend exposes these REST endpoints (all require a valid JWT except `/user/login`):

| Prefix | Description |
|---|---|
| `/user` | Login / logout |
| `/api/persons` | People (names, contact info) |
| `/api/clients` | Clients (sponsors students, holds credit balance) |
| `/api/students` | Students (skill level, age, teaching requirements) |
| `/api/instructors` | Instructors (hourly rate, restrictions, blocked times) |
| `/api/credentials` | Instructor credentials (musical, CPR, special-ed, etc.) |
| `/api/compatibility` | Instructor-student compatibility checks and overrides |
| `/api/rooms` | Rooms (capacity, instruments, blocked times) |
| `/api/lessons` | Standalone lesson templates and occurrence enrollment |
| `/api/lessons/<id>/project` | Project a lesson's recurrence into occurrences |
| `/api/lessons/occurrences/<id>/enroll` | Enroll a student in a specific occurrence |
| `/api/courses` | Course programs (group classes, lesson series) |
| `/api/courses/<id>/project` | Project a course's recurrence into occurrences |
| `/api/invoices` | Invoices and line items (lesson charges, instrument fees, etc.) |
| `/api/payments` | Record and manage payments |
| `/api/attendance-policies` | Charge rules for absences and late cancellations |
| `/api/audit` | Audit log (admin only) |

---

## Stopping and Restarting

- To **stop:** press `Ctrl + C` in each Command Prompt window
- To **restart the backend:** `cd` to the project folder and run `python backend\app.py`
- To **restart the frontend:** `cd` to `frontend` and run `npm run dev`

You do **not** need to re-run `pip install` or `npm install` unless new packages were added.

---

## Troubleshooting

**"python is not recognised"**
Python was not added to PATH. Re-run the Python installer and tick "Add Python to PATH".

**"npm is not recognised"**
Node.js was not installed correctly. Re-run the installer.

**Login fails with "Invalid credentials"**
Check the SHA-256 hash was generated correctly (Step 4) and that `.env` has the correct Supabase URL and key.

**The website loads but shows "Could not load data"**
The backend is not running. Start it again (Step 7).

**Port 5000 is already in use**
In `backend/app.py`, change `app.run(debug=True)` to `app.run(debug=True, port=5001)` and update `NEXT_PUBLIC_API_BASE` in `.env.local` to use port 5001.

**"No module named 'backend'"**
You must run the server from the project root folder (`YourMusicDepot`), not from inside the `backend` folder. The `python backend\app.py` command handles this automatically.

---

## Running Tests (Optional)

```
cd %USERPROFILE%\Desktop\YourMusicDepot
python -m pytest backend/tests -v
```

You should see passing tests and a few skipped ones. No tests should fail if setup is correct.
