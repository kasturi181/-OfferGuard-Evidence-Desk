create table if not exists public.reports (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  risk_level text,
  input_text text,
  report jsonb not null
);
alter table public.reports enable row level security;
-- No policies: only the backend service-role key can read/write.
