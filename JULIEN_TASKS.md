# Frontend Tasks — Julien

Zach says thanks for picking these up. Below is everything needed to finish and polish the frontend. No scope expansion — just completing what's already started.

---

## How to Work

Follow the patterns already established in the codebase:

| Pattern | Copy from |
|---|---|
| List page + DataTable | `features/students/` or `features/clients/` |
| Detail page structure | `app/(dashboard)/students/[studentId]/page.tsx` |
| InfoCard component | `features/students/components/StudentInfoCard.tsx` |
| Custom detail hook | `features/students/hooks/use_student_detail.ts` |
| API fetch layer | `features/students/api/student_detail.ts` |
| Create/Edit modal | `features/students/components/StudentModal.tsx` |

Each feature folder follows the same structure: `api/`, `components/`, `hooks/`.

---

## Priority 1 — Missing Core Pages

### 1. Instructor Detail Page — `/instructors/[instructorId]`

The instructor list exists but clicking a row goes nowhere. Build the detail page following the exact client/student pattern.

- `features/instructors/api/instructor_detail.ts` — fetch single instructor + their credentials
- `features/instructors/hooks/use_instructor_detail.ts`
- `features/instructors/components/InstructorInfoCard.tsx` — name, email, phone, rate, status
- `features/instructors/components/InstructorDetailTabs.tsx` with tabs:
  - **Credentials** — list credential cards (type, proficiencies, valid from/until); add/remove credential modal
  - **Schedule** — upcoming lesson occurrences
  - **Students** — current enrolled students across active courses/lessons
  - **Compatibility** — preferred/disliked/blocked students with reason
- Wire instructor list rows to navigate to this page

---

### 2. Room Detail Page — `/rooms/[roomId]`

Same situation as instructors — list exists, no detail page.

- `features/rooms/api/room_detail.ts`
- `features/rooms/hooks/use_room_detail.ts`
- `features/rooms/components/RoomInfoCard.tsx` — name, capacity, instruments, blocked times
- `features/rooms/components/RoomDetailTabs.tsx` with tabs:
  - **Upcoming Sessions** — lesson occurrences in this room (date, time, instructor, students)
  - **Blocked Times** — view/add blocked time windows
- Wire room list rows to navigate to this page

---

### 3. Courses Section — `/courses` + `/courses/[courseId]`

Courses is a new entity in the backend. It needs the full treatment.

- Add **Courses** to the sidebar nav (between Instructors and Rooms)
- Create `features/courses/` with the full `api/`, `components/`, `hooks/` structure
- `/courses` list page — DataTable columns: name, instructor, period, status, enrolled/capacity
- Create/Edit course modal fields:
  - Name, description
  - Room (dropdown)
  - Instructor(s) (multi-select)
  - Date range (period start / period end)
  - Recurrence — cron expression or ISO date (text input is fine for now)
  - Start time / End time
  - Rate (charge type: one_time or hourly, amount)
  - Required instruments (list)
  - Capacity (number)
  - Skill range (min level / max level)
- `/courses/[courseId]` detail page:
  - **InfoCard** — name, period, room, lead instructor, status
  - **Roster tab** — enrolled students; enroll/unenroll student buttons
  - **Schedule tab** — projected occurrences table; **"Project Schedule"** button → `POST /api/courses/<id>/project`
  - **Instructors tab** — add/remove instructors
  - **Rate tab** — display charge type and amount

---

## Priority 2 — Polish Existing Pages

### 4. Lessons — Occurrence-Based Enrollment

The enrollment flow needs to move from lesson → occurrence.

- Add a **"Project Schedule"** button on lesson detail → calls `POST /api/lessons/<id>/project`
- Show projected occurrences in a table below the lesson info
- Clicking an occurrence opens an enrollment modal (select student)
- Add attendance recording per occurrence: Present / Absent / Late-Cancel
- API endpoints to use:
  - `POST /api/lessons/<id>/project`
  - `POST /api/lessons/occurrences/<id>/enroll`
  - `DELETE /api/lessons/occurrences/<id>/enroll/<student_id>`
  - `PUT /api/lessons/occurrences/<id>/enroll/<student_id>/attendance`

---

### 5. Student Form — New Fields

- Add `age` number input to the student create/edit modal
- Add a **Teaching Requirements** list builder — each entry has:
  - Type: `credential` | `min_student_age` | `max_student_age`
  - Value (text or number depending on type)
- Add a **Compatibility tab** on the student detail page:
  - List existing overrides (instructor name, verdict badge, reason)
  - "Add Override" button → modal: select instructor, verdict (blocked/disliked/preferred/required), reason
  - API: `POST /api/compatibility`, `DELETE /api/compatibility/<id>`

---

### 6. Instructor Form — New Fields

- Add a **Teaching Restrictions** list builder to the create/edit modal — same structure as student requirements (min/max student age)
- Add `credential_type` dropdown to the credential add modal:
  - Options: `musical`, `cpr`, `special_ed`, `vulnerable_sector`, `first_aid`, `other`

---

### 7. Invoices Page — `/invoices`

- Add **Invoices** to the sidebar
- List page — DataTable columns: client, student, status, total, created date
- Invoice detail (drawer or separate page):
  - Header: client, student, status, total
  - **Line Items** table: description, item type badge, amount
  - **"Add Charge"** button → modal for non-lesson charges:
    - Item type: `instrument_damage` | `instrument_purchase` | `other`
    - Description (text)
    - Amount (number)
    - API: `POST /api/invoices/<id>/line-items`
  - Action buttons: Mark Paid, Cancel

---

### 8. Payments Page Polish

- Add search/filter by client name or invoice number
- Link each payment row to its invoice
- Show `payment_method` column (it's stored in the backend but not displayed)

---

### 9. Compatibility Check UI

Can live as a tab inside the student and instructor detail pages (see tasks 5 and 6) or as a standalone page — your call.

- Select student + instructor
- Run check → `GET /api/compatibility/check?student_id=&instructor_id=`
- Display result: verdict badge (OK / Blocked / Requirement Not Met), reasons list
- List all existing overrides for the selected student/instructor

---

## Priority 3 — Settings & QoL

### 10. Settings Page — Edit Functionality

Currently display-only. Add:
- **Change Password** form → calls the auth/user endpoint
- Optionally: change display name / username

---

### 11. Global Polish

- Loading skeletons on all detail pages (not just spinners)
- Consistent empty states on all tables: e.g. "No courses yet — create one"
- All modals should close and refresh the list on successful save
- Toast notifications for destructive actions (delete instructor, cancel invoice, etc.)
- Mobile responsiveness pass on sidebar and DataTable components

---

## API Reference

All endpoints require a valid JWT in the `Authorization: Bearer <token>` header except `POST /user/login`.

| Endpoint | Description |
|---|---|
| `GET /api/instructors` | List all instructors |
| `GET /api/instructors/<id>` | Get instructor detail |
| `GET /api/credentials?instructor_id=<id>` | Get credentials for instructor |
| `POST /api/credentials` | Add credential |
| `DELETE /api/credentials/<id>` | Remove credential |
| `GET /api/rooms` | List all rooms |
| `GET /api/rooms/<id>` | Get room detail |
| `GET /api/courses` | List all courses |
| `POST /api/courses` | Create course |
| `GET /api/courses/<id>` | Get course detail |
| `PUT /api/courses/<id>` | Update course |
| `DELETE /api/courses/<id>` | Delete course |
| `POST /api/courses/<id>/project` | Project recurrence into occurrences |
| `POST /api/courses/<id>/students` | Enroll student in course |
| `DELETE /api/courses/<id>/students/<student_id>` | Unenroll student |
| `POST /api/courses/<id>/instructors` | Add instructor to course |
| `DELETE /api/courses/<id>/instructors/<instructor_id>` | Remove instructor |
| `POST /api/lessons/<id>/project` | Project lesson recurrence into occurrences |
| `POST /api/lessons/occurrences/<id>/enroll` | Enroll student in occurrence |
| `DELETE /api/lessons/occurrences/<id>/enroll/<student_id>` | Unenroll from occurrence |
| `PUT /api/lessons/occurrences/<id>/enroll/<student_id>/attendance` | Record attendance |
| `GET /api/compatibility/check?student_id=&instructor_id=` | Run compatibility check |
| `GET /api/compatibility/instructors?student_id=` | List compatible instructors for student |
| `POST /api/compatibility` | Set compatibility override |
| `DELETE /api/compatibility/<id>` | Remove override |
| `POST /api/invoices/<id>/line-items` | Add non-lesson charge to invoice |
| `GET /api/invoices` | List invoices |
| `GET /api/invoices/<id>` | Get invoice detail |
