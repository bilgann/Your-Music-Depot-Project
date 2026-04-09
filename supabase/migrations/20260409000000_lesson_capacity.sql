-- Add per-lesson capacity so each lesson can set its own student limit,
-- independent of the room's overall capacity.
alter table lesson add column if not exists capacity integer;
