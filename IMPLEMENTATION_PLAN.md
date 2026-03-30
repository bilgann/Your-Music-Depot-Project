# Frontend Implementation Plan

Based on [JULIEN_TASKS.md](JULIEN_TASKS.md) — full audit of missing work against the current codebase.

---

## Codebase Status Summary

| Feature | List Page | Detail Page | CRUD Modal | API Layer | Notes |
|---------|-----------|-------------|------------|-----------|-------|
| Students | ✅ | ✅ | ✅ | ✅ | Missing: `age`, teaching requirements, compatibility tab |
| Clients | ✅ | ✅ | ✅ | ✅ | Complete |
| Instructors | ✅ | ❌ | ✅ (basic) | ✅ (partial) | Missing: detail page, credentials, restrictions |
| Rooms | ✅ | ❌ | ✅ (basic) | ✅ (partial) | Missing: detail page, blocked times |
| Courses | ❌ | ❌ | ❌ | ❌ | Entirely missing |
| Invoices | ❌ | ❌ | ❌ | ⚠️ (generate only) | Only `generateInvoice()` exists |
| Payments | ✅ | — | ✅ (create only) | ✅ | Missing: search/filter, invoice link, `payment_method` column already shown |
| Scheduling | ✅ (calendar) | — | ✅ (lesson modal) | ✅ (CRUD) | Missing: project schedule, occurrence enrollment, attendance |
| Settings | ✅ (display) | — | — | — | Missing: change password form |

---

## Established Patterns to Follow

All new code must replicate these conventions already in the codebase:

- **API layer**: One file per entity in `features/<entity>/api/`. Uses `apiFetch` / `apiJson` / `apiJsonPaged` from `lib/api.ts`.
- **Hooks**: `use_<entity>s.ts` for list (pagination + search), `use_<entity>_detail.ts` for detail data, `use_<entity>_crud.ts` for modal/form state.
- **Components**: `<Entity>InfoCard.tsx`, `<Entity>DetailTabs.tsx`, tab content components.
- **Pages**: `app/(dashboard)/<entity>/page.tsx` for list, `app/(dashboard)/<entity>/[<entityId>]/page.tsx` for detail.
- **UI primitives**: `DataTable`, `Modal`, `Navbar`, `DataState`, `Sections`, `InfoCard`, `Button`, `TextField`, `NumberField`, `SelectField`, `Combobox`.

---

## Priority 1 — Missing Core Pages

### Task 1: Instructor Detail Page — `/instructors/[instructorId]`

The instructor list page exists with basic CRUD. Clicking a row does nothing. Need full detail page.

#### 1.1 — API: Instructor detail + credentials
**File**: `features/instructors/api/instructor_detail.ts` (new)

| Function | Endpoint | Returns |
|----------|----------|---------|
| `getInstructorById(id)` | `GET /api/instructors/<id>` | Instructor with full info (name, email, phone, rate, status) |
| `getInstructorCredentials(id)` | `GET /api/credentials?instructor_id=<id>` | Credential[] |
| `addCredential(data)` | `POST /api/credentials` | Credential |
| `removeCredential(id)` | `DELETE /api/credentials/<id>` | void |
| `getInstructorSchedule(id)` | TBD — filter `/api/lessons` by instructor_id or use detail response | LessonOccurrence[] |
| `getInstructorStudents(id)` | Derive from course/lesson enrollments in detail response | Student[] |
| `getInstructorCompatibility(id)` | `GET /api/compatibility/instructors?student_id=` or parse from detail | Override[] |

**Types to define** (in same file or `types/index.ts`):
```ts
type Credential = {
    credential_id: string;
    instructor_id: string;
    credential_type: string; // musical | cpr | special_ed | vulnerable_sector | first_aid | other
    proficiencies: string[];
    valid_from: string | null;
    valid_until: string | null;
};

type CompatibilityOverride = {
    override_id: string;
    student_id: string;
    instructor_id: string;
    verdict: string; // blocked | disliked | preferred | required
    reason: string | null;
    student_name?: string;
    instructor_name?: string;
};
```

#### 1.2 — Hook: `use_instructor_detail.ts` (new)
**File**: `features/instructors/hooks/use_instructor_detail.ts`

- Fetch instructor, credentials, schedule, students, compatibility in parallel on mount
- Return `{ instructor, credentials, schedule, students, compatibility, loading, error, refresh }`
- Follow the exact pattern of `use_student_detail.ts`

#### 1.3 — Components (all new)

| File | Purpose |
|------|---------|
| `features/instructors/components/instructor_info_card.tsx` | Name, email, phone, rate, status — uses `InfoCard` |
| `features/instructors/components/instructor_detail_tabs.tsx` | Wrapper with `Sections` for 4 tabs |
| `features/instructors/components/instructor_credentials_tab.tsx` | List credential cards; "Add Credential" button opens modal |
| `features/instructors/components/instructor_schedule_tab.tsx` | Table of upcoming lesson occurrences |
| `features/instructors/components/instructor_students_tab.tsx` | Table of currently enrolled students |
| `features/instructors/components/instructor_compatibility_tab.tsx` | List overrides (student name, verdict badge, reason) |
| `features/instructors/components/credential_modal.tsx` | Modal: type dropdown, proficiencies, valid from/until |

#### 1.4 — Page
**File**: `app/(dashboard)/instructors/[instructorId]/page.tsx` (new)

- Follow student detail page pattern exactly
- `useParams()` → `instructorId`
- `Navbar` with back to `/instructors`
- `DataState` → `InstructorInfoCard` → `Sections` with 4 tabs

#### 1.5 — Wire list row click
**File**: `app/(dashboard)/instructors/page.tsx` (edit)

- Add `onRowClick` to `DataTable` → `router.push(/instructors/${inst.instructor_id})`

**Estimated files**: 2 existing edits + 9 new files

---

### Task 2: Room Detail Page — `/rooms/[roomId]`

#### 2.1 — API: Room detail
**File**: `features/rooms/api/room_detail.ts` (new)

| Function | Endpoint | Returns |
|----------|----------|---------|
| `getRoomById(id)` | `GET /api/rooms/<id>` | Room (name, capacity, instruments, blocked_times) |

**Notes**: Upcoming sessions and blocked times may come from the room detail response or separate endpoints. Handle both.

#### 2.2 — Hook: `use_room_detail.ts` (new)
**File**: `features/rooms/hooks/use_room_detail.ts`

- Fetch room detail on mount
- Return `{ room, upcomingSessions, blockedTimes, loading, error, refresh }`

#### 2.3 — Components (all new)

| File | Purpose |
|------|---------|
| `features/rooms/components/room_info_card.tsx` | Name, capacity, instruments, blocked time summary — uses `InfoCard` |
| `features/rooms/components/room_detail_tabs.tsx` | `Sections` with 2 tabs |
| `features/rooms/components/room_sessions_tab.tsx` | Table: date, time, instructor, students |
| `features/rooms/components/room_blocked_times_tab.tsx` | Table of blocked windows + "Add Blocked Time" button/modal |
| `features/rooms/components/blocked_time_modal.tsx` | Modal: start datetime, end datetime, reason |

#### 2.4 — Page
**File**: `app/(dashboard)/rooms/[roomId]/page.tsx` (new)

#### 2.5 — Wire list row click
**File**: `app/(dashboard)/rooms/page.tsx` (edit)

- Add `onRowClick` → `router.push(/rooms/${room.room_id})`

**Estimated files**: 2 existing edits + 7 new files

---

### Task 3: Courses Section — Full Feature

This is the largest task. Courses is completely absent from the frontend.

#### 3.1 — Sidebar: Add Courses nav item
**File**: `components/layout/sidebar.tsx` (edit)

- Add `{ label: "Courses", path: "/courses", icon: faBook }` between Instructors and Rooms in `NAV_ITEMS`
- Import `faBook` from `@fortawesome/free-solid-svg-icons`

#### 3.2 — API layer
**File**: `features/courses/api/course.ts` (new)

| Function | Endpoint | Method |
|----------|----------|--------|
| `listCourses(page, pageSize, search)` | `/api/courses` | GET |
| `getCourseById(id)` | `/api/courses/<id>` | GET |
| `createCourse(data)` | `/api/courses` | POST |
| `updateCourse(id, data)` | `/api/courses/<id>` | PUT |
| `deleteCourse(id)` | `/api/courses/<id>` | DELETE |
| `projectSchedule(id)` | `/api/courses/<id>/project` | POST |
| `enrollStudent(courseId, studentId)` | `/api/courses/<id>/students` | POST |
| `unenrollStudent(courseId, studentId)` | `/api/courses/<id>/students/<student_id>` | DELETE |
| `addInstructor(courseId, instructorId)` | `/api/courses/<id>/instructors` | POST |
| `removeInstructor(courseId, instructorId)` | `/api/courses/<id>/instructors/<instructor_id>` | DELETE |

**Types to define**:
```ts
type Course = {
    course_id: string;
    name: string;
    description: string | null;
    room_id: string | null;
    room?: { room_id: string; name: string };
    instructor_ids: string[];
    instructors?: Instructor[];
    period_start: string;
    period_end: string;
    recurrence: string | null;
    start_time: string;
    end_time: string;
    charge_type: "one_time" | "hourly";
    rate_amount: number;
    required_instruments: string[];
    capacity: number;
    skill_min: number | null;
    skill_max: number | null;
    status: string;
    enrolled_count?: number;
};

type CourseOccurrence = {
    occurrence_id: string;
    course_id: string;
    date: string;
    start_time: string;
    end_time: string;
    status: string;
};
```

#### 3.3 — Hooks

| File | Purpose |
|------|---------|
| `features/courses/hooks/use_courses.ts` | List with pagination + search |
| `features/courses/hooks/use_course_crud.ts` | Create/edit modal form state (all fields from task spec) |
| `features/courses/hooks/use_course_detail.ts` | Fetch course + roster + occurrences + instructors |

#### 3.4 — Components

| File | Purpose |
|------|---------|
| `features/courses/components/course_info_card.tsx` | Name, period, room, lead instructor, status |
| `features/courses/components/course_detail_tabs.tsx` | `Sections`: Roster, Schedule, Instructors, Rate |
| `features/courses/components/course_roster_tab.tsx` | Enrolled students table + enroll/unenroll buttons |
| `features/courses/components/course_schedule_tab.tsx` | Projected occurrences table + "Project Schedule" button |
| `features/courses/components/course_instructors_tab.tsx` | Add/remove instructors |
| `features/courses/components/course_rate_tab.tsx` | Display charge type + amount |
| `features/courses/components/course_modal.tsx` | Full create/edit modal with all fields |
| `features/courses/components/enroll_student_modal.tsx` | Select student to enroll in course |

#### 3.5 — Pages

| File | Purpose |
|------|---------|
| `app/(dashboard)/courses/page.tsx` (new) | List page with DataTable + CRUD modal |
| `app/(dashboard)/courses/[courseId]/page.tsx` (new) | Detail page with tabs |

**Estimated files**: 1 existing edit (sidebar) + 13 new files

---

## Priority 2 — Polish Existing Pages

### Task 4: Lessons — Occurrence-Based Enrollment

The lesson calendar + modal exist. Need to add occurrence projection and enrollment.

#### 4.1 — API: Lesson occurrence endpoints
**File**: `features/scheduling/api/lesson.ts` (edit — add functions)

| Function | Endpoint | Method |
|----------|----------|--------|
| `projectLessonSchedule(lessonId)` | `/api/lessons/<id>/project` | POST |
| `enrollInOccurrence(occurrenceId, studentId)` | `/api/lessons/occurrences/<id>/enroll` | POST |
| `unenrollFromOccurrence(occurrenceId, studentId)` | `/api/lessons/occurrences/<id>/enroll/<student_id>` | DELETE |
| `recordAttendance(occurrenceId, studentId, status)` | `/api/lessons/occurrences/<id>/enroll/<student_id>/attendance` | PUT |

**Types to add**:
```ts
type LessonOccurrence = {
    occurrence_id: string;
    lesson_id: string;
    date: string;
    start_time: string;
    end_time: string;
    status: string;
    enrollments?: OccurrenceEnrollment[];
};

type OccurrenceEnrollment = {
    student_id: string;
    student_name: string;
    attendance_status: string | null; // Present | Absent | Late-Cancel
};
```

#### 4.2 — Components (new)

| File | Purpose |
|------|---------|
| `features/scheduling/components/lesson_occurrences_table.tsx` | Table of projected occurrences below lesson info |
| `features/scheduling/components/occurrence_enrollment_modal.tsx` | Select student to enroll in a specific occurrence |
| `features/scheduling/components/attendance_modal.tsx` | Record attendance: Present / Absent / Late-Cancel |

#### 4.3 — Integration
**Where**: Modify the lesson calendar or add a lesson detail view. The "Project Schedule" button and occurrences table could be added to the lesson edit modal or a new dedicated lesson detail page.

**Decision point**: The calendar currently doesn't have a detail page per lesson. Options:
- **Option A**: Add a drawer/expanded view within the calendar that shows occurrences when a lesson is clicked
- **Option B**: Create a lesson detail page at `/scheduling/[lessonId]`

**Recommendation**: Option A (drawer/panel) to keep the scheduling flow integrated, but Option B is simpler. Choosing **Option B** to stay consistent with the detail page pattern.

**New files**:
| File | Purpose |
|------|---------|
| `features/scheduling/hooks/use_lesson_detail.ts` | Fetch lesson + occurrences |
| `app/(dashboard)/scheduling/[lessonId]/page.tsx` | Lesson detail with occurrences table |

**Estimated files**: 1 existing edit + 5 new files

---

### Task 5: Student Form — New Fields

#### 5.1 — Add `age` to student create/edit modal
**File**: `features/students/hooks/use_student_crud.ts` (edit)

- Add `age: ""` to initial form state
- Include `age` in create/update payloads

**File**: `app/(dashboard)/students/page.tsx` (edit)

- Add `<NumberField label="Age" ...>` to the student modal

#### 5.2 — Teaching Requirements list builder
**File**: `features/students/components/teaching_requirements_builder.tsx` (new)

- Dynamic list of rows: `{ type: "credential" | "min_student_age" | "max_student_age", value: string }`
- "Add Requirement" button appends a row
- Each row: type dropdown + value input + remove button
- Integrate into student create/edit modal

#### 5.3 — Compatibility tab on student detail
**File**: `features/students/components/student_compatibility_tab.tsx` (new)

- Table: instructor name, verdict badge (color-coded), reason
- "Add Override" button → modal

**File**: `features/students/components/compatibility_override_modal.tsx` (new)

- Select instructor (dropdown/combobox), verdict select (blocked/disliked/preferred/required), reason text
- API: `POST /api/compatibility`

**File**: `features/students/api/student.ts` (edit) — or new `features/students/api/compatibility.ts`

- `getStudentCompatibility(studentId)`
- `addCompatibilityOverride(data)`
- `removeCompatibilityOverride(overrideId)` → `DELETE /api/compatibility/<id>`

**File**: `features/students/hooks/use_student_detail.ts` (edit)

- Add compatibility data fetch
- Return `compatibility` in hook output

**File**: `app/(dashboard)/students/[studentId]/page.tsx` (edit)

- Add "Compatibility" tab to `Sections`

**Estimated files**: 3 existing edits + 3 new files

---

### Task 6: Instructor Form — New Fields

#### 6.1 — Teaching Restrictions list builder
**File**: `features/instructors/components/teaching_restrictions_builder.tsx` (new)

- Same structure as student teaching requirements: `{ type: "min_student_age" | "max_student_age", value: string }`
- Integrate into instructor create/edit modal

**File**: `app/(dashboard)/instructors/page.tsx` (edit)

- Add restrictions builder to Modal

**File**: `features/instructors/hooks/use_instructor_crud.ts` (edit)

- Add `restrictions: []` to form state
- Include in create/update payloads

#### 6.2 — Credential type dropdown
This is handled in the credential modal (Task 1.3 — `credential_modal.tsx`). Ensure the credential form includes:
- `credential_type` dropdown: `musical`, `cpr`, `special_ed`, `vulnerable_sector`, `first_aid`, `other`

**Estimated files**: 2 existing edits + 1 new file

---

### Task 7: Invoices Page — `/invoices`

#### 7.1 — Sidebar: Add Invoices nav item
**File**: `components/layout/sidebar.tsx` (edit)

- Add `{ label: "Invoices", path: "/invoices", icon: faFileInvoiceDollar }` after Payments

#### 7.2 — API layer
**File**: `features/invoices/api/invoice.ts` (edit — expand significantly)

| Function | Endpoint | Method |
|----------|----------|--------|
| `listInvoices(page, pageSize, search)` | `/api/invoices` | GET |
| `getInvoiceById(id)` | `/api/invoices/<id>` | GET |
| `addLineItem(invoiceId, data)` | `/api/invoices/<id>/line-items` | POST |

**Types**:
```ts
type Invoice = {
    invoice_id: string;
    client_id: string;
    student_id: string;
    client_name?: string;
    student_name?: string;
    status: string;
    total_amount: number;
    amount_paid: number;
    period_start: string;
    period_end: string;
    created_at: string;
    line_items?: InvoiceLineItem[];
};

type InvoiceLineItem = {
    line_item_id: string;
    invoice_id: string;
    description: string;
    item_type: string; // lesson | instrument_damage | instrument_purchase | other
    amount: number;
};
```

#### 7.3 — Hooks

| File | Purpose |
|------|---------|
| `features/invoices/hooks/use_invoices.ts` (new) | List with pagination + search |
| `features/invoices/hooks/use_invoice_detail.ts` (new) | Fetch invoice with line items |
| `features/invoices/hooks/use_invoice_actions.ts` (new) | Mark Paid, Cancel, Add Charge modal state |

#### 7.4 — Components

| File | Purpose |
|------|---------|
| `features/invoices/components/invoice_detail.tsx` (new) | Header (client, student, status, total) + line items table |
| `features/invoices/components/add_charge_modal.tsx` (new) | Item type dropdown, description, amount |

**Decision**: Detail as a drawer or separate page?
- **Recommendation**: Separate page at `/invoices/[invoiceId]` for consistency with the rest of the app.

#### 7.5 — Pages

| File | Purpose |
|------|---------|
| `app/(dashboard)/invoices/page.tsx` (new) | List: DataTable with client, student, status, total, created date |
| `app/(dashboard)/invoices/[invoiceId]/page.tsx` (new) | Detail: header + line items + action buttons |

**Estimated files**: 2 existing edits (sidebar, invoice API) + 7 new files

---

### Task 8: Payments Page Polish

#### 8.1 — Add search/filter
**File**: `app/(dashboard)/payments/page.tsx` (edit)

- The `usePayments` hook currently has no search support — add search param
- Add `search` / `onSearchChange` to the `Navbar`

**File**: `features/payments/hooks/use_payments.ts` (edit)

- Add `search` state + pass to API
- Filter by client name or invoice number

#### 8.2 — Link payment row to invoice
**File**: `app/(dashboard)/payments/page.tsx` (edit)

- Add `onRowClick` → navigate to `/invoices/${p.invoice_id}`
- Or make the Invoice column a clickable link

#### 8.3 — Show `payment_method` column
**Status**: Already shown! The current payments page already has a "Method" column displaying `p.payment_method`. **No work needed here.**

**Estimated files**: 2 existing edits

---

### Task 9: Compatibility Check UI

#### Decision: Standalone page vs. embedded in detail pages

The compatibility tab is already being added to student detail (Task 5.3) and instructor detail (Task 1.3). A standalone check tool can be an additional page or a section within those tabs.

**Recommendation**: Add a "Check Compatibility" button on both the student and instructor compatibility tabs that opens a modal.

#### 9.1 — API
**File**: `features/students/api/compatibility.ts` (new — or merge into existing)

| Function | Endpoint |
|----------|----------|
| `checkCompatibility(studentId, instructorId)` | `GET /api/compatibility/check?student_id=&instructor_id=` |
| `getCompatibleInstructors(studentId)` | `GET /api/compatibility/instructors?student_id=` |
| `listOverrides(studentId?, instructorId?)` | Derived from existing endpoints |
| `createOverride(data)` | `POST /api/compatibility` |
| `deleteOverride(id)` | `DELETE /api/compatibility/<id>` |

#### 9.2 — Components
**File**: `features/students/components/compatibility_check_modal.tsx` (new)

- Select student + instructor (combobox)
- "Run Check" button → calls API
- Display result: verdict badge (OK / Blocked / Requirement Not Met), reasons list
- Show all existing overrides for the pair

This modal can be reused on both student and instructor detail pages.

**Estimated files**: 1–2 new files

---

## Priority 3 — Settings & QoL

### Task 10: Settings Page — Edit Functionality

**File**: `app/(dashboard)/settings/page.tsx` (edit)

Currently: display-only, decodes JWT to show username/role/user_id.

#### 10.1 — Change Password form
- Add form section: current password, new password, confirm new password
- Submit → `PUT` or `POST` to auth/user endpoint (need to confirm endpoint from backend)
- Show success/error toast

#### 10.2 — Change display name (optional per task spec)
- Add editable username field
- Submit to user update endpoint

**Estimated files**: 1 existing edit, possibly 1 new hook file

---

### Task 11: Global Polish

#### 11.1 — Loading skeletons
**Files to edit**: All detail pages (student, client, instructor, room, course, invoice)

- Replace spinner/loading text with skeleton components
- Create a reusable `Skeleton` component if not already present, or use CSS shimmer

**File**: `components/ui/skeleton.tsx` (new — optional utility)

#### 11.2 — Consistent empty states
**Files to edit**: All DataTable usages

- Verify all tables have meaningful `emptyMessage` props (most already do)
- Add contextual empty messages with action hints: "No courses yet — create one"

#### 11.3 — Modal close + list refresh
**Status**: Already implemented in existing CRUD hooks (modal closes on success, calls `refresh()`). Verify this pattern is followed in all new code.

#### 11.4 — Toast notifications
**File**: Add a toast system (new)

- `components/ui/toast.tsx` — Toast component + context provider
- Wire into destructive actions: delete instructor, cancel invoice, etc.
- Options: lightweight custom implementation or integrate a library like `react-hot-toast`

#### 11.5 — Mobile responsiveness
**Files to edit**: `components/layout/sidebar.tsx`, `components/ui/data_table.tsx`, `globals.css`

- Sidebar: collapsible hamburger menu on mobile
- DataTable: horizontal scroll or card layout on small screens

**Estimated files**: 2–4 new files, 6+ existing edits

---

## Implementation Order (Recommended)

Work in this order to maximize unblocking and minimize rework:

| Phase | Tasks | Rationale |
|-------|-------|-----------|
| **Phase 1** | Sidebar update (3.1 + 7.1) | One-time edit; unblocks all new pages |
| **Phase 2** | Courses full feature (3.2–3.5) | Largest task, no dependencies on other frontend work |
| **Phase 3** | Instructor detail (1.1–1.5) | Second largest, includes credentials UI |
| **Phase 4** | Room detail (2.1–2.5) | Smaller version of instructor pattern |
| **Phase 5** | Invoices page (7.2–7.5) | Unblocks payment linking (Task 8) |
| **Phase 6** | Lesson occurrences (4.1–4.3) | Builds on existing scheduling feature |
| **Phase 7** | Student form enhancements (5.1–5.3) | Smaller scope, adds fields + tab |
| **Phase 8** | Instructor form enhancements (6.1–6.2) | Small scope |
| **Phase 9** | Payments polish (8.1–8.2) | Depends on invoices page existing to link to |
| **Phase 10** | Compatibility check UI (9.1–9.2) | Depends on compatibility tabs from Tasks 5 & 1 |
| **Phase 11** | Settings edit (10.1–10.2) | Independent, small |
| **Phase 12** | Global polish (11.1–11.5) | Last — cross-cutting, touches all pages |

---

## File Change Summary

| Category | New Files | Edited Files |
|----------|-----------|-------------|
| Task 1: Instructor Detail | 9 | 2 |
| Task 2: Room Detail | 7 | 2 |
| Task 3: Courses | 13 | 1 |
| Task 4: Lesson Occurrences | 5 | 1 |
| Task 5: Student Enhancements | 3 | 3 |
| Task 6: Instructor Enhancements | 1 | 2 |
| Task 7: Invoices | 7 | 2 |
| Task 8: Payments Polish | 0 | 2 |
| Task 9: Compatibility Check | 2 | 0 |
| Task 10: Settings | 0–1 | 1 |
| Task 11: Global Polish | 2–4 | 6+ |
| **TOTAL** | **~49–52** | **~22+** |

---

## Key Risks & Open Questions

1. **Backend API shape**: The exact response structure for `GET /api/courses/<id>`, `GET /api/rooms/<id>`, and `GET /api/instructors/<id>` needs to be verified. The types above are inferred from the task spec — adjust once actual API responses are confirmed.

2. **Lesson detail vs. calendar integration (Task 4)**: The current scheduling UX is entirely calendar-based. Adding occurrence projection requires either a detail page or a panel. Decision above recommends a detail page, but this could change based on UX preference.

3. **Compatibility API coverage (Task 9)**: The `GET /api/compatibility/instructors?student_id=` endpoint is listed but may not return the full override list. Need to verify.

4. **Auth endpoint for password change (Task 10)**: The auth API only has `login` and `logout`. The backend endpoint for password change needs to be confirmed.

5. **Course modal complexity (Task 3)**: The course create/edit form has many fields (name, description, room dropdown, multi-select instructors, date range, recurrence, time, rate, instruments, capacity, skill range). This will be the most complex modal in the app. Consider a multi-step form or grouping fields into sections.

6. **Toast system (Task 11.4)**: No toast infrastructure exists. Need to choose between custom implementation or a lightweight library.
