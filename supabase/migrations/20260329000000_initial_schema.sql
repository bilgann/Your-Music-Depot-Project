-- =============================================================================
-- Your Music Depot — Full Schema Migration
-- Updated: 2026-03-29  (domain-aligned rewrite)
-- =============================================================================
-- Run this in the Supabase SQL Editor to build the schema from scratch.
-- It is safe to re-run: every DROP uses CASCADE so dependent objects are
-- cleaned up in the right order.
-- =============================================================================


-- =============================================================================
-- DROP (reverse-dependency order — deepest dependents first)
-- =============================================================================

drop table if exists audit_log                        cascade;
drop table if exists credit_transaction               cascade;
drop table if exists payment                          cascade;
drop table if exists invoice_line                     cascade;
drop table if exists invoice                          cascade;
drop table if exists instructor_student_compatibility cascade;
drop table if exists credential                       cascade;
drop table if exists lesson_enrollment                cascade;
drop table if exists lesson_occurrence                cascade;
drop table if exists lesson                           cascade;
drop table if exists course                           cascade;
drop table if exists student                          cascade;
drop table if exists client                           cascade;
drop table if exists attendance_policy                cascade;
drop table if exists skill                            cascade;
drop table if exists room                             cascade;
drop table if exists instructor                       cascade;
drop table if exists person                           cascade;
drop table if exists app_user                         cascade;

-- Legacy table names from old schema
drop table if exists lessons    cascade;
drop table if exists instructors cascade;
drop table if exists rooms      cascade;
drop table if exists students   cascade;
drop table if exists users      cascade;

-- Enable UUID generation
create extension if not exists "pgcrypto";


-- =============================================================================
-- INDEPENDENT TABLES
-- =============================================================================

-- Application users (staff / admin logins)
-- Password stored as SHA-256 hex digest of the plaintext password.
create table app_user (
    user_id       uuid primary key default gen_random_uuid(),
    username      text not null unique,
    password_hash text not null,
    role          text not null default 'admin'
                      check (role in ('admin', 'instructor'))
);

-- Shared identity — a person record can be linked to both a client and a student
create table person (
    person_id uuid primary key default gen_random_uuid(),
    name      text not null,
    email     text,
    phone     text
);

-- Instructors are linked to a person record for contact information.
-- blocked_times  jsonb array of BlockedTime objects (holiday, vacation, recurring)
-- restrictions   jsonb array of TeachingRequirement objects
--                (e.g. {"requirement_type":"min_student_age","value":"5"})
create table instructor (
    instructor_id uuid    primary key default gen_random_uuid(),
    person_id     uuid    not null references person (person_id) on delete restrict,
    hourly_rate   numeric,                            -- CAD per hour
    blocked_times jsonb   not null default '[]'::jsonb,
    restrictions  jsonb   not null default '[]'::jsonb
);

-- Physical rooms / studios
-- instruments   jsonb array of RoomInstrument objects
-- blocked_times jsonb array of BlockedTime objects
create table room (
    room_id       uuid    primary key default gen_random_uuid(),
    name          text    not null,
    capacity      integer,
    instruments   jsonb   not null default '[]'::jsonb,
    blocked_times jsonb   not null default '[]'::jsonb
);

-- Skills / disciplines catalogue (Piano, Guitar, …) — optional reference data
create table skill (
    skill_id    uuid primary key default gen_random_uuid(),
    name        text not null,
    description text
);

-- Attendance charge policies
-- charge_type: 'none' | 'flat' | 'percentage'
-- Only one policy can be the school-wide default (enforced by partial unique index below)
create table attendance_policy (
    policy_id                uuid    primary key default gen_random_uuid(),
    name                     text    not null,
    absent_charge_type       text    not null default 'none'
                                 check (absent_charge_type in ('none','flat','percentage')),
    absent_charge_value      numeric not null default 0,
    cancel_charge_type       text    not null default 'none'
                                 check (cancel_charge_type in ('none','flat','percentage')),
    cancel_charge_value      numeric not null default 0,
    late_cancel_charge_type  text    not null default 'none'
                                 check (late_cancel_charge_type in ('none','flat','percentage')),
    late_cancel_charge_value numeric not null default 0,
    is_default               boolean not null default false
);

create unique index uq_attendance_policy_default
    on attendance_policy (is_default)
    where is_default = true;


-- =============================================================================
-- PERSON-DERIVED ROLE TABLES
-- =============================================================================

-- Clients — parents / guardians / account holders
-- blocked_times covers household-level unavailability (family holidays, etc.)
create table client (
    client_id     uuid    primary key default gen_random_uuid(),
    person_id     uuid    not null references person (person_id) on delete restrict,
    credits       numeric not null default 0,          -- prepaid credit wallet
    blocked_times jsonb   not null default '[]'::jsonb
);

-- Students — learners, always linked to a person; optionally to a client/guardian
-- instrument_skill_levels  jsonb array of per-instrument skill levels
--                          (e.g. {"name":"Piano","family":"keyboard","skill_level":"intermediate"})
-- age                      integer — used by CompatibilityService for instructor age restrictions
-- requirements             jsonb array of TeachingRequirement objects
--                          (e.g. {"requirement_type":"credential","value":"cpr"})
create table student (
    student_id               uuid    primary key default gen_random_uuid(),
    person_id                uuid    not null references person  (person_id) on delete restrict,
    client_id                uuid             references client  (client_id) on delete set null,
    instrument_skill_levels  jsonb   not null default '[]'::jsonb,
    age                      integer          check (age > 0),
    requirements             jsonb   not null default '[]'::jsonb
);


-- =============================================================================
-- COURSE (top-level program aggregate)
-- =============================================================================
-- A course is the template for a recurring series of sessions (group classes,
-- private lesson series, one-off workshops).  Individual sessions are materialised
-- as lesson_occurrence rows by the ScheduleProjectionService.
--
-- instructor_ids  uuid[] — ordered list; [0] is the lead instructor
-- student_ids     uuid[] — enrolled roster; maintained by the application layer
-- recurrence      text   — cron expression OR ISO date for one-time courses
-- start_time      text   — HH:MM, same for all occurrences unless rescheduled
-- end_time        text   — HH:MM
-- rate            jsonb  — {charge_type, amount, currency}
-- required_instruments jsonb array
-- skill_range     jsonb  — {min_level, max_level}

create table course (
    course_id             uuid   primary key default gen_random_uuid(),
    name                  text   not null,
    description           text,
    room_id               uuid   not null references room (room_id) on delete restrict,
    instructor_ids        uuid[] not null default '{}',
    student_ids           uuid[] not null default '{}',
    period_start          date   not null,
    period_end            date   not null,
    recurrence            text   not null,
    start_time            text   not null,
    end_time              text   not null,
    rate                  jsonb,
    required_instruments  jsonb  not null default '[]'::jsonb,
    capacity              integer,
    skill_range           jsonb,
    status                text   not null default 'draft'
                              check (status in ('draft','active','completed','cancelled')),
    created_at            timestamptz not null default now(),
    constraint course_period_valid check (period_end >= period_start)
);


-- =============================================================================
-- LESSON (standalone lesson template)
-- =============================================================================
-- A lesson is a recurring or one-time private lesson template that is NOT part
-- of a course.  It may optionally link to a parent course (course_id).
-- Individual sessions are materialised as lesson_occurrence rows.
--
-- start_time / end_time  text HH:MM — the template time (date comes from occurrence)
-- student_ids            uuid[] — enrolled student roster (typically 1 for private)
-- recurrence             text  — cron expression OR ISO date

create table lesson (
    lesson_id            uuid    primary key default gen_random_uuid(),
    instructor_id        uuid    not null references instructor       (instructor_id) on delete restrict,
    room_id              uuid    not null references room             (room_id)       on delete restrict,
    course_id            uuid             references course           (course_id)     on delete set null,
    attendance_policy_id uuid             references attendance_policy (policy_id)   on delete set null,
    start_time           text    not null,    -- HH:MM
    end_time             text    not null,    -- HH:MM
    student_ids          uuid[]  not null default '{}',
    rate                 numeric,
    status               text,
    recurrence           text               -- cron expression or ISO date
);


-- =============================================================================
-- LESSON OCCURRENCE (materialised session)
-- =============================================================================
-- A single concrete session on a specific date, generated from either a lesson
-- template or a course.  Exactly one of lesson_id / course_id must be set
-- (enforced by the check constraint below).
--
-- status  text: Scheduled | Completed | Cancelled | Rescheduled

create table lesson_occurrence (
    occurrence_id    uuid    primary key default gen_random_uuid(),
    lesson_id        uuid             references lesson  (lesson_id)  on delete cascade,
    course_id        uuid             references course  (course_id)  on delete cascade,
    date             date    not null,
    start_time       text    not null,   -- HH:MM
    end_time         text    not null,   -- HH:MM
    instructor_id    uuid    not null references instructor (instructor_id) on delete restrict,
    room_id          uuid    not null references room       (room_id)       on delete restrict,
    status           text    not null default 'Scheduled'
                         check (status in ('Scheduled','Completed','Cancelled','Rescheduled')),
    rate             numeric,
    is_rescheduled   boolean not null default false,
    cancelled_reason text,
    constraint occurrence_has_single_source check (
        (lesson_id is not null)::int + (course_id is not null)::int = 1
    )
);


-- =============================================================================
-- LESSON ENROLLMENT
-- =============================================================================
-- Many-to-many: student ↔ occurrence with per-student attendance tracking.
-- attendance_status: Present | Absent | Cancelled | Late Cancel | Excused

create table lesson_enrollment (
    enrollment_id      uuid   primary key default gen_random_uuid(),
    occurrence_id      uuid   not null references lesson_occurrence (occurrence_id) on delete cascade,
    student_id         uuid   not null references student           (student_id)    on delete cascade,
    attendance_status  text            check (attendance_status in
                                           ('Present','Absent','Cancelled','Late Cancel','Excused')),
    enrolled_at        timestamptz not null default now(),
    constraint uq_lesson_enrollment unique (occurrence_id, student_id)
);


-- =============================================================================
-- CREDENTIALS
-- =============================================================================
-- Teaching credentials held by an instructor.
-- credential_type: musical | cpr | special_ed | vulnerable_sector | first_aid | other
-- proficiencies: jsonb array of InstrumentProficiency objects

create table credential (
    credential_id   uuid  primary key default gen_random_uuid(),
    instructor_id   uuid  not null references instructor (instructor_id) on delete cascade,
    credential_type text  not null default 'musical'
                        check (credential_type in
                               ('musical','cpr','special_ed','vulnerable_sector','first_aid','other')),
    proficiencies   jsonb not null default '[]'::jsonb,
    valid_from      date,
    valid_until     date,
    issued_by       text,
    issued_date     date
);


-- =============================================================================
-- INSTRUCTOR–STUDENT COMPATIBILITY
-- =============================================================================
-- Explicit preference or restriction between a specific instructor and student.
-- verdict: blocked | disliked | preferred | required
-- initiated_by: student | instructor | admin

create table instructor_student_compatibility (
    compatibility_id uuid   primary key default gen_random_uuid(),
    instructor_id    uuid   not null references instructor (instructor_id) on delete cascade,
    student_id       uuid   not null references student   (student_id)    on delete cascade,
    verdict          text   not null check (verdict in ('blocked','disliked','preferred','required')),
    reason           text   not null default '',
    initiated_by     text   not null check (initiated_by in ('student','instructor','admin')),
    created_at       timestamptz not null default now(),
    constraint uq_compatibility unique (instructor_id, student_id)
);


-- =============================================================================
-- BILLING
-- =============================================================================

-- Monthly invoices generated per student
create table invoice (
    invoice_id   uuid    primary key default gen_random_uuid(),
    student_id   uuid             references student (student_id) on delete set null,
    client_id    uuid             references client  (client_id)  on delete set null,
    period_start date    not null,
    period_end   date    not null,
    total_amount numeric not null default 0,   -- denormalised sum of invoice_line.amount
    amount_paid  numeric not null default 0,
    status       text    not null default 'Pending'
                     check (status in ('Pending','Paid','Overdue','Cancelled')),
    created_at   timestamptz not null default now(),
    constraint invoice_period_valid check (period_end >= period_start),
    constraint invoice_no_duplicate unique (student_id, period_start)
);

-- Line items within an invoice
-- item_type: lesson | instrument_damage | instrument_purchase | other
-- occurrence_id links to the lesson_occurrence for "lesson" items (nullable for others)
create table invoice_line (
    line_id           uuid    primary key default gen_random_uuid(),
    invoice_id        uuid    not null references invoice          (invoice_id)   on delete cascade,
    occurrence_id     uuid             references lesson_occurrence (occurrence_id) on delete set null,
    item_type         text    not null default 'lesson'
                          check (item_type in ('lesson','instrument_damage','instrument_purchase','other')),
    description       text    not null,
    amount            numeric not null default 0,
    attendance_status text             check (attendance_status in
                                           ('Present','Absent','Cancelled','Late Cancel','Excused'))
);

-- Payments applied against invoices
create table payment (
    payment_id     uuid    primary key default gen_random_uuid(),
    invoice_id     uuid    not null references invoice (invoice_id) on delete restrict,
    amount         numeric not null,
    payment_method text    not null default 'Card',
    paid_on        date,
    notes          text
);


-- =============================================================================
-- CLIENT CREDITS LEDGER
-- =============================================================================
-- Immutable audit trail of every credit balance change for a client.
-- payment_method is set when the transaction relates to an invoice payment.

create table credit_transaction (
    transaction_id uuid        primary key default gen_random_uuid(),
    client_id      uuid        not null references client  (client_id)  on delete cascade,
    invoice_id     uuid                 references invoice (invoice_id) on delete set null,
    amount         numeric     not null,   -- positive = credit added, negative = credit spent
    reason         text,
    payment_method text,
    created_at     timestamptz not null default now()
);


-- =============================================================================
-- AUDIT LOG
-- =============================================================================

create table audit_log (
    log_id      uuid        primary key default gen_random_uuid(),
    user_id     uuid                 references app_user (user_id) on delete set null,
    action      text        not null check (action in ('CREATE','UPDATE','DELETE','UPSERT')),
    entity_type text        not null,
    entity_id   text,
    old_value   jsonb,
    new_value   jsonb,
    created_at  timestamptz not null default now()
);


-- =============================================================================
-- INDEXES
-- =============================================================================

-- instructor
create index idx_instructor_person         on instructor (person_id);

-- room (no extra indexes needed beyond PK)

-- student
create index idx_student_person            on student (person_id);
create index idx_student_client            on student (client_id);

-- client
create index idx_client_person             on client (person_id);

-- course
create index idx_course_room               on course (room_id);
create index idx_course_status             on course (status);
create index idx_course_period             on course (period_start, period_end);

-- lesson
create index idx_lesson_instructor         on lesson (instructor_id);
create index idx_lesson_room               on lesson (room_id);
create index idx_lesson_course             on lesson (course_id);

-- lesson_occurrence
create index idx_occurrence_lesson         on lesson_occurrence (lesson_id);
create index idx_occurrence_course         on lesson_occurrence (course_id);
create index idx_occurrence_instructor     on lesson_occurrence (instructor_id);
create index idx_occurrence_date           on lesson_occurrence (date);
create index idx_occurrence_status         on lesson_occurrence (status);

-- lesson_enrollment
create index idx_enrollment_occurrence     on lesson_enrollment (occurrence_id);
create index idx_enrollment_student        on lesson_enrollment (student_id);

-- credential
create index idx_credential_instructor     on credential (instructor_id);
create index idx_credential_type           on credential (credential_type);
create index idx_credential_valid_until    on credential (valid_until);

-- instructor_student_compatibility
create index idx_compat_instructor         on instructor_student_compatibility (instructor_id);
create index idx_compat_student            on instructor_student_compatibility (student_id);

-- invoice
create index idx_invoice_student           on invoice (student_id);
create index idx_invoice_client            on invoice (client_id);
create index idx_invoice_status            on invoice (status);
create index idx_invoice_period_start      on invoice (period_start);

-- invoice_line
create index idx_invoice_line_invoice      on invoice_line (invoice_id);
create index idx_invoice_line_occurrence   on invoice_line (occurrence_id);

-- payment
create index idx_payment_invoice           on payment (invoice_id);

-- credit_transaction
create index idx_credit_txn_client         on credit_transaction (client_id);
create index idx_credit_txn_invoice        on credit_transaction (invoice_id);
create index idx_credit_txn_created        on credit_transaction (created_at desc);

-- audit_log
create index idx_audit_entity              on audit_log (entity_type, entity_id);
create index idx_audit_user                on audit_log (user_id);
create index idx_audit_created             on audit_log (created_at desc);


-- =============================================================================
-- ROW-LEVEL SECURITY
-- Authentication is enforced at the Flask API layer (@require_auth decorator).
-- RLS is disabled so the anon/service key can read and write freely.
-- =============================================================================

alter table app_user                         disable row level security;
alter table person                           disable row level security;
alter table instructor                       disable row level security;
alter table room                             disable row level security;
alter table skill                            disable row level security;
alter table attendance_policy                disable row level security;
alter table client                           disable row level security;
alter table student                          disable row level security;
alter table course                           disable row level security;
alter table lesson                           disable row level security;
alter table lesson_occurrence                disable row level security;
alter table lesson_enrollment                disable row level security;
alter table credential                       disable row level security;
alter table instructor_student_compatibility disable row level security;
alter table invoice                          disable row level security;
alter table invoice_line                     disable row level security;
alter table payment                          disable row level security;
alter table credit_transaction               disable row level security;
alter table audit_log                        disable row level security;
