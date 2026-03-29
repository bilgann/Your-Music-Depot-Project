-- =============================================================================
-- Your Music Depot — Full Schema Migration
-- Generated: 2026-03-29
-- =============================================================================
-- WARNING: This drops all existing tables and recreates them from scratch.
-- Run this once against your Supabase project via the SQL Editor.
-- =============================================================================

-- Drop old schema (order matters — dependent tables first)
drop table if exists audit_log          cascade;
drop table if exists credit_transaction cascade;
drop table if exists payment            cascade;
drop table if exists invoice_line       cascade;
drop table if exists invoice            cascade;
drop table if exists lesson_enrollment  cascade;
drop table if exists lesson             cascade;
drop table if exists student            cascade;
drop table if exists client             cascade;
drop table if exists instructor         cascade;
drop table if exists room               cascade;
drop table if exists skill              cascade;
drop table if exists attendance_policy  cascade;
drop table if exists person             cascade;
drop table if exists app_user           cascade;
-- Legacy table names from old schema
drop table if exists lessons            cascade;
drop table if exists instructors        cascade;
drop table if exists rooms              cascade;
drop table if exists students           cascade;
drop table if exists users              cascade;

-- Enable UUID generation
create extension if not exists "pgcrypto";


-- =============================================================================
-- INDEPENDENT TABLES (no foreign key dependencies)
-- =============================================================================

-- Application users (staff / admin logins)
create table if not exists app_user (
    user_id       uuid primary key default gen_random_uuid(),
    username      text not null unique,
    password_hash text not null,              -- SHA-256 hex digest
    role          text not null default 'admin'
);

-- Shared identity record — a person can be both a client and a student
create table if not exists person (
    person_id uuid primary key default gen_random_uuid(),
    name      text not null,
    email     text,
    phone     text
);

-- Instructors are kept separate from the person/user hierarchy
create table if not exists instructor (
    instructor_id uuid primary key default gen_random_uuid(),
    name          text not null,
    email         text,
    phone         text
);

-- Physical rooms / studios
create table if not exists room (
    room_id  uuid primary key default gen_random_uuid(),
    name     text not null,
    capacity integer
);

-- Skills / disciplines (e.g. Piano, Guitar) — optional catalogue
create table if not exists skill (
    skill_id    uuid primary key default gen_random_uuid(),
    name        text not null,
    description text
);

-- Attendance charge policies (absent / cancelled / late-cancel rules)
create table if not exists attendance_policy (
    policy_id              uuid    primary key default gen_random_uuid(),
    name                   text    not null,
    -- absent
    absent_charge_type     text    not null default 'none'
                               check (absent_charge_type in ('none', 'flat', 'percentage')),
    absent_charge_value    numeric not null default 0,
    -- regular cancel
    cancel_charge_type     text    not null default 'none'
                               check (cancel_charge_type in ('none', 'flat', 'percentage')),
    cancel_charge_value    numeric not null default 0,
    -- late cancel
    late_cancel_charge_type  text    not null default 'none'
                                 check (late_cancel_charge_type in ('none', 'flat', 'percentage')),
    late_cancel_charge_value numeric not null default 0,
    -- only one policy may be the school-wide default
    is_default             boolean not null default false
);

-- Enforce a single default policy at the DB level
create unique index if not exists uq_attendance_policy_default
    on attendance_policy (is_default)
    where is_default = true;


-- =============================================================================
-- PERSON-DERIVED ROLE TABLES
-- =============================================================================

-- Clients — parents / guardians / account holders
create table if not exists client (
    client_id uuid    primary key default gen_random_uuid(),
    person_id uuid    not null references person (person_id) on delete restrict,
    credits   numeric not null default 0           -- prepaid credit wallet balance
);

-- Students — learners (always linked to a person; optionally to a client/guardian)
create table if not exists student (
    student_id uuid primary key default gen_random_uuid(),
    person_id  uuid not null references person  (person_id) on delete restrict,
    client_id  uuid          references client  (client_id) on delete set null
);


-- =============================================================================
-- LESSON & ENROLLMENT
-- =============================================================================

-- Individual lesson instances
create table if not exists lesson (
    lesson_id           uuid      primary key default gen_random_uuid(),
    instructor_id       uuid      not null references instructor       (instructor_id) on delete restrict,
    room_id             uuid      not null references room             (room_id)       on delete restrict,
    attendance_policy_id uuid               references attendance_policy (policy_id)  on delete set null,
    -- legacy direct student link (kept for single-student lessons; use lesson_enrollment for multi-student)
    student_id          uuid               references student          (student_id)   on delete set null,
    start_time          timestamptz not null,
    end_time            timestamptz not null,
    rate                numeric,
    status              text,                -- e.g. 'Scheduled', 'Completed', 'Cancelled'
    recurrence          text,                -- cron expression, e.g. '0 10 * * 1'
    constraint lesson_end_after_start check (end_time > start_time)
);

-- Many-to-many student ↔ lesson with per-student attendance tracking
create table if not exists lesson_enrollment (
    enrollment_id     uuid      primary key default gen_random_uuid(),
    lesson_id         uuid      not null references lesson   (lesson_id)  on delete cascade,
    student_id        uuid      not null references student  (student_id) on delete cascade,
    attendance_status text,                  -- 'Present' | 'Absent' | 'Cancelled' | 'Late Cancel' | 'Excused'
    enrolled_at       timestamptz default now(),
    constraint uq_lesson_enrollment unique (lesson_id, student_id)
);


-- =============================================================================
-- BILLING
-- =============================================================================

-- Monthly invoices generated per student
create table if not exists invoice (
    invoice_id   uuid    primary key default gen_random_uuid(),
    student_id   uuid    references student (student_id) on delete set null,
    client_id    uuid    references client  (client_id)  on delete set null,
    period_start date    not null,
    period_end   date    not null,
    total_amount numeric not null default 0,
    amount_paid  numeric not null default 0,
    status       text    not null default 'Pending',     -- 'Pending' | 'Paid' | 'Overdue'
    constraint invoice_period_valid check (period_end >= period_start),
    constraint invoice_no_duplicate unique (student_id, period_start)
);

-- Line items within an invoice (one row per lesson)
create table if not exists invoice_line (
    line_id           uuid    primary key default gen_random_uuid(),
    invoice_id        uuid    not null references invoice (invoice_id) on delete cascade,
    lesson_id         uuid             references lesson  (lesson_id)  on delete set null,
    description       text    not null,
    amount            numeric not null default 0,
    attendance_status text             -- snapshot of status at invoice generation time
);

-- Payments applied against invoices
create table if not exists payment (
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

-- Immutable audit trail of every credit balance change for a client
create table if not exists credit_transaction (
    transaction_id uuid        primary key default gen_random_uuid(),
    client_id      uuid        not null references client  (client_id)  on delete cascade,
    invoice_id     uuid                 references invoice (invoice_id) on delete set null,
    amount         numeric     not null,   -- positive = credit added, negative = credit spent
    reason         text,
    created_at     timestamptz not null default now()
);


-- =============================================================================
-- AUDIT LOG
-- =============================================================================

create table if not exists audit_log (
    log_id      uuid        primary key default gen_random_uuid(),
    user_id     uuid        references app_user (user_id) on delete set null,
    action      text        not null,   -- 'CREATE' | 'UPDATE' | 'DELETE'
    entity_type text        not null,   -- table name, e.g. 'lesson'
    entity_id   text,                   -- stringified PK of the affected row
    old_value   jsonb,
    new_value   jsonb,
    created_at  timestamptz not null default now()
);


-- =============================================================================
-- INDEXES  (beyond the implicit PK indexes)
-- =============================================================================

-- Lessons — common filter patterns
create index if not exists idx_lesson_instructor    on lesson (instructor_id);
create index if not exists idx_lesson_room          on lesson (room_id);
create index if not exists idx_lesson_start_time    on lesson (start_time);
create index if not exists idx_lesson_status        on lesson (status);

-- Enrollments
create index if not exists idx_enrollment_lesson    on lesson_enrollment (lesson_id);
create index if not exists idx_enrollment_student   on lesson_enrollment (student_id);

-- Students / clients
create index if not exists idx_student_client       on student (client_id);
create index if not exists idx_student_person       on student (person_id);
create index if not exists idx_client_person        on client  (person_id);

-- Invoices
create index if not exists idx_invoice_student      on invoice (student_id);
create index if not exists idx_invoice_client       on invoice (client_id);
create index if not exists idx_invoice_status       on invoice (status);
create index if not exists idx_invoice_period_start on invoice (period_start);

-- Payments
create index if not exists idx_payment_invoice      on payment (invoice_id);

-- Credits ledger
create index if not exists idx_credit_txn_client    on credit_transaction (client_id);
create index if not exists idx_credit_txn_created   on credit_transaction (created_at desc);

-- Audit log
create index if not exists idx_audit_entity         on audit_log (entity_type, entity_id);
create index if not exists idx_audit_user           on audit_log (user_id);
create index if not exists idx_audit_created        on audit_log (created_at desc);


-- =============================================================================
-- ROW-LEVEL SECURITY
-- Authentication is enforced at the Flask API layer (@require_auth decorator).
-- RLS is disabled on all tables so the anon/service key can read and write freely.
-- =============================================================================

alter table app_user           disable row level security;
alter table person             disable row level security;
alter table instructor         disable row level security;
alter table room               disable row level security;
alter table skill              disable row level security;
alter table attendance_policy  disable row level security;
alter table client             disable row level security;
alter table student            disable row level security;
alter table lesson             disable row level security;
alter table lesson_enrollment  disable row level security;
alter table invoice            disable row level security;
alter table invoice_line       disable row level security;
alter table payment            disable row level security;
alter table credit_transaction disable row level security;
alter table audit_log          disable row level security;
