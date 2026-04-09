-- Add blocked_times support to student
alter table student
    add column if not exists blocked_times jsonb not null default '[]'::jsonb;
