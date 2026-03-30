-- =============================================================================
-- School Schedule — school-wide blocked times with per-entity overrides
-- =============================================================================

create table school_schedule (
    schedule_id      uuid        primary key default gen_random_uuid(),
    label            text        not null,
    block_type       text        not null default 'school'
                         check (block_type in ('holiday','vacation','school','other')),
    date             date,
    date_range_start date,
    date_range_end   date,
    recurrence       text,
    is_active        boolean     not null default true,
    created_at       timestamptz not null default now(),

    -- Exactly one scheduling mode must be set
    constraint school_schedule_one_type check (
        (date is not null)::int
      + (date_range_start is not null and date_range_end is not null)::int
      + (recurrence is not null)::int
      = 1
    ),
    constraint school_schedule_range_valid check (
        date_range_end is null or date_range_end >= date_range_start
    )
);

-- Overrides: exempt a specific entity from a school schedule entry.
-- entity_type is polymorphic (no FK constraint on entity_id).
create table school_schedule_override (
    override_id  uuid        primary key default gen_random_uuid(),
    schedule_id  uuid        not null references school_schedule (schedule_id) on delete cascade,
    entity_type  text        not null
                     check (entity_type in ('instructor','room','lesson','course')),
    entity_id    uuid        not null,
    reason       text        not null default '',
    created_at   timestamptz not null default now(),
    constraint uq_schedule_override unique (schedule_id, entity_type, entity_id)
);

create index idx_school_schedule_active on school_schedule (is_active);
create index idx_school_override_schedule on school_schedule_override (schedule_id);
create index idx_school_override_entity on school_schedule_override (entity_type, entity_id);

alter table school_schedule          disable row level security;
alter table school_schedule_override disable row level security;
