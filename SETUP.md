# Your Music Depot — Setup Guide

This guide will get both the backend (server) and frontend (website) running on your computer. No technical experience needed — just follow each step in order.

---

## What You Will Need

Before starting, download and install these three programs. Each link goes to the official download page.

### 1. Python 3.12
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

You need to create two extra tables in Supabase that are not created automatically.

1. In your Supabase project, click **SQL Editor** in the left sidebar
2. Click **New query**
3. Copy and paste the following SQL into the editor, then click **Run**:

```sql
-- User accounts table
CREATE TABLE IF NOT EXISTS app_user (
    user_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    username  text UNIQUE NOT NULL,
    password  text NOT NULL,   -- SHA-256 hex digest
    role      text NOT NULL DEFAULT 'instructor' CHECK (role IN ('admin', 'instructor'))
);

-- Audit log table (tracks all changes to data)
CREATE TABLE IF NOT EXISTS audit_log (
    id          bigserial PRIMARY KEY,
    user_id     uuid,
    action      text NOT NULL CHECK (action IN ('CREATE', 'UPDATE', 'DELETE')),
    entity_type text NOT NULL,
    entity_id   text,
    old_value   jsonb,
    new_value   jsonb,
    created_at  timestamptz NOT NULL DEFAULT now()
);
```

---

## Step 4 — Create Your First Admin User

You need to add yourself as an admin user in the database. The password must be stored as a SHA-256 hash (a scrambled version of your password).

### Generate a password hash

Open Command Prompt and run:
```
python -c "import hashlib; print(hashlib.sha256('YourPasswordHere'.encode()).hexdigest())"
```

Replace `YourPasswordHere` with the password you want to use. Copy the long string of letters and numbers that gets printed — that is your hashed password.

### Insert the user into Supabase

1. Back in the Supabase **SQL Editor**, click **New query**
2. Paste this, replacing the placeholders:

```sql
INSERT INTO app_user (username, password, role)
VALUES ('your_username', 'paste_hash_here', 'admin');
```

3. Click **Run**

---

## Step 5 — Get Your Supabase Keys

1. In your Supabase project, click **Project Settings** (gear icon) in the left sidebar
2. Click **API**
3. You will see two values you need:
   - **Project URL** — looks like `https://xxxxxxxxxxx.supabase.co`
   - **anon public** key — a long string starting with `eyJ...`

Keep this tab open — you will need these values in the next step.

---

## Step 6 — Configure the Backend

1. Open the `YourMusicDepot` folder on your Desktop
2. Open the `backend` folder inside it
3. Create a new file called `.env` (the name starts with a dot, no other extension)
   - Right-click inside the folder → New → Text Document
   - Name it `.env` (when Windows asks "are you sure?", click Yes)
4. Open `.env` with Notepad and paste in the following, replacing the values with your Supabase details:

```
SUPABASE_URL=https://xxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJyour_anon_key_here
JWT_SECRET=pick-any-long-random-string-here-at-least-32-characters
```

For `JWT_SECRET`, just type any long random phrase — for example: `my-music-depot-secret-key-2024-secure`. This is used to sign login tokens.

Save the file.

---

## Step 7 — Start the Backend Server

Open Command Prompt and run these commands one at a time:

```
cd %USERPROFILE%\Desktop\YourMusicDepot
python -m pip install -r backend\requirements.txt
python backend\app.py
```

The first command moves into the project folder.
The second installs all the required packages (only needed once).
The third starts the server.

You should see output ending with something like:
```
 * Running on http://127.0.0.1:5000
```

**Leave this Command Prompt window open.** The server must keep running while you use the app.

---

## Step 8 — Configure the Frontend

1. Open the `frontend` folder inside `YourMusicDepot`
2. Create a new file called `.env.local` (same way as before — New Text Document, rename to `.env.local`)
3. Open it with Notepad and paste:

```
NEXT_PUBLIC_API_BASE=http://127.0.0.1:5000
```

Save the file.

---

## Step 9 — Start the Frontend

Open a **second** Command Prompt window (the first one must stay open running the backend).

Run these commands one at a time:

```
cd %USERPROFILE%\Desktop\YourMusicDepot\frontend
npm install
npm run dev
```

The first command moves into the frontend folder.
The second installs packages (only needed once).
The third starts the website.

You should see output like:
```
  ▲ Next.js
  - Local: http://localhost:3000
```

---

## Step 10 — Open the App

Open your web browser and go to:
```
http://localhost:3000
```

You will see the login page. Log in with the username and password you created in Step 4.

> **Temporary dev account:** If you have not created a Supabase user yet, you can log in with username `barnes` and password `password`. This is a development account — **remove or disable it before using this app for real data** by deleting the fallback code in `backend/app/models/user.py`.

---

## Stopping and Restarting

- To **stop** the app: press `Ctrl + C` in each Command Prompt window
- To **restart** the backend: open Command Prompt, `cd` to the project folder, run `python backend\app.py`
- To **restart** the frontend: open Command Prompt, `cd` to the `frontend` folder, run `npm run dev`

You do **not** need to run `pip install` or `npm install` again after the first time, unless the project is updated with new packages.

---

## Troubleshooting

**"python is not recognised"**
Python was not added to PATH during installation. Re-run the Python installer and tick "Add Python to PATH".

**"npm is not recognised"**
Node.js was not installed correctly. Re-run the Node.js installer.

**Login fails with "Invalid credentials"**
Check that you generated the SHA-256 hash correctly (Step 4) and that the `.env` file has the correct Supabase URL and key.

**The website loads but shows "Could not load data"**
The backend server is not running. Open Command Prompt and start it again (Step 7).

**Port 5000 is already in use**
Another program is using that port. In `backend/app.py`, change `app.run(debug=True)` to `app.run(debug=True, port=5001)` and update `.env.local` in the frontend to use port 5001.

---

## Running Tests (Optional)

To verify everything is working correctly:

```
cd %USERPROFILE%\Desktop\YourMusicDepot
python -m pytest backend/tests -v
```

You should see a mix of passing tests and a few skipped ones (marked with `s`). No tests should fail if the setup is correct.
