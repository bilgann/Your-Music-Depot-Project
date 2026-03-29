-- Run in Supabase SQL Editor
-- Adds missing columns required by invoice generation and display features.

alter table if exists public.invoice
    add column if not exists period_start date;

alter table if exists public.invoice
    add column if not exists period_end date;

alter table if exists public.invoice_line
    add column if not exists lesson_id bigint;

-- Optional index for lookups from generate_monthly_invoice and joins
create index if not exists idx_invoice_line_lesson_id
    on public.invoice_line (lesson_id);
