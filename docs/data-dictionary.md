# Your Music Depot Data Dictionary

This dictionary captures the operational schema expected by backend services and frontend features.
All fields include Type, Size, Nullability, and Default.

## instructor

| Column | Type | Size | Null | Default | Notes |
|---|---|---|---|---|---|
| instructor_id | bigint | 8 bytes | NO | auto-generated identity | Primary key |
| name | varchar | 255 | NO | none | Instructor full name |
| email | varchar | 255 | YES | null | Unique business email recommended |
| phone | varchar | 32 | YES | null | Contact number |
| created_at | timestamptz | 8 bytes | YES | now() | Audit timestamp |

## student

| Column | Type | Size | Null | Default | Notes |
|---|---|---|---|---|---|
| student_id | bigint | 8 bytes | NO | auto-generated identity | Primary key |
| name | varchar | 255 | NO | none | Student full name |
| email | varchar | 255 | YES | null | Unique business email recommended |
| phone | varchar | 32 | YES | null | Contact number |
| created_at | timestamptz | 8 bytes | YES | now() | Audit timestamp |

## room

| Column | Type | Size | Null | Default | Notes |
|---|---|---|---|---|---|
| room_id | bigint | 8 bytes | NO | auto-generated identity | Primary key |
| name | varchar | 120 | NO | none | Room display name |
| capacity | integer | 4 bytes | NO | 1 | Max concurrent students |
| created_at | timestamptz | 8 bytes | YES | now() | Audit timestamp |

## lesson

| Column | Type | Size | Null | Default | Notes |
|---|---|---|---|---|---|
| lesson_id | bigint | 8 bytes | NO | auto-generated identity | Primary key |
| instructor_id | bigint | 8 bytes | NO | none | FK to instructor.instructor_id |
| student_id | bigint | 8 bytes | NO | none | FK to student.student_id |
| room_id | bigint | 8 bytes | NO | none | FK to room.room_id |
| instrument | varchar | 80 | NO | none | Instrument/topic |
| lesson_type | varchar | 20 | NO | 'private' | private/group |
| date | date | 4 bytes | NO | none | Calendar day |
| start_time | timestamptz | 8 bytes | NO | none | Lesson start |
| end_time | timestamptz | 8 bytes | NO | none | Lesson end |
| status | varchar | 20 | NO | 'Scheduled' | Scheduled/Completed/Cancelled |
| rate | numeric(10,2) | 10 digits, 2 decimals | YES | 0.00 | Hourly or per-lesson rate |
| created_at | timestamptz | 8 bytes | YES | now() | Audit timestamp |

## lesson_enrollment

| Column | Type | Size | Null | Default | Notes |
|---|---|---|---|---|---|
| lesson_enrollment_id | bigint | 8 bytes | NO | auto-generated identity | Primary key |
| lesson_id | bigint | 8 bytes | NO | none | FK to lesson.lesson_id |
| student_id | bigint | 8 bytes | NO | none | FK to student.student_id |
| created_at | timestamptz | 8 bytes | YES | now() | Enrollment timestamp |

## instructor_skill

| Column | Type | Size | Null | Default | Notes |
|---|---|---|---|---|---|
| instructor_skill_id | bigint | 8 bytes | NO | auto-generated identity | Primary key |
| instructor_id | bigint | 8 bytes | NO | none | FK to instructor.instructor_id |
| skill | varchar | 80 | NO | none | Instrument/skill name |
| min_skill_level | integer | 4 bytes | NO | 1 | Minimum student level required |
| created_at | timestamptz | 8 bytes | YES | now() | Audit timestamp |

## student_skill

| Column | Type | Size | Null | Default | Notes |
|---|---|---|---|---|---|
| student_skill_id | bigint | 8 bytes | NO | auto-generated identity | Primary key |
| student_id | bigint | 8 bytes | NO | none | FK to student.student_id |
| skill | varchar | 80 | NO | none | Instrument/skill name |
| skill_level | integer | 4 bytes | NO | 1 | Student proficiency level |
| created_at | timestamptz | 8 bytes | YES | now() | Audit timestamp |

## invoice

| Column | Type | Size | Null | Default | Notes |
|---|---|---|---|---|---|
| invoice_id | bigint | 8 bytes | NO | auto-generated identity | Primary key |
| student_id | bigint | 8 bytes | NO | none | FK to student.student_id |
| period_start | date | 4 bytes | YES | null | Billing period start |
| period_end | date | 4 bytes | YES | null | Billing period end |
| issued_on | date | 4 bytes | YES | current_date | Invoice issue date |
| due_on | date | 4 bytes | YES | null | Invoice due date |
| total_amount | numeric(10,2) | 10 digits, 2 decimals | NO | 0.00 | Total billed amount |
| amount_paid | numeric(10,2) | 10 digits, 2 decimals | NO | 0.00 | Paid amount to date |
| status | varchar | 20 | NO | 'Pending' | Pending/Paid/Cancelled |
| created_at | timestamptz | 8 bytes | YES | now() | Audit timestamp |

## invoice_line

| Column | Type | Size | Null | Default | Notes |
|---|---|---|---|---|---|
| invoice_line_id | bigint | 8 bytes | NO | auto-generated identity | Primary key |
| invoice_id | bigint | 8 bytes | NO | none | FK to invoice.invoice_id |
| lesson_id | bigint | 8 bytes | YES | null | FK to lesson.lesson_id |
| description | varchar | 255 | YES | null | Human-readable line description |
| quantity | numeric(10,2) | 10 digits, 2 decimals | NO | 1.00 | Quantity multiplier |
| unit_price | numeric(10,2) | 10 digits, 2 decimals | NO | 0.00 | Unit rate |
| amount | numeric(10,2) | 10 digits, 2 decimals | NO | 0.00 | Line total |
| created_at | timestamptz | 8 bytes | YES | now() | Audit timestamp |

## payment

| Column | Type | Size | Null | Default | Notes |
|---|---|---|---|---|---|
| payment_id | bigint | 8 bytes | NO | auto-generated identity | Primary key |
| invoice_id | bigint | 8 bytes | NO | none | FK to invoice.invoice_id |
| amount | numeric(10,2) | 10 digits, 2 decimals | NO | none | Payment amount |
| payment_method | varchar | 30 | YES | 'Card' | Card/Cash/Transfer |
| paid_on | date | 4 bytes | YES | current_date | Payment date |
| notes | text | variable | YES | null | Optional note |
| created_at | timestamptz | 8 bytes | YES | now() | Audit timestamp |
