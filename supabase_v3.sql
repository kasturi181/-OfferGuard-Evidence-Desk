-- OfferGuard schema v3. Run in Supabase SQL Editor. Safe to re-run.
-- Order: supabase.sql (existing) -> this file. supabase_v2.sql is replaced by this file.

-- 1. submissions: one row per analysis request
create table if not exists public.submissions (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  source text not null default 'paste' check (source in ('paste', 'pdf')),
  input_redacted text,                 -- null unless STORE_INPUT_TEXT=true; emails/phones removed
  input_sha256 text not null,
  char_count int not null check (char_count >= 0),
  simulate_failure boolean not null default false
);

-- 2. extracted_fields: one row per extracted value
create table if not exists public.extracted_fields (
  id uuid primary key default gen_random_uuid(),
  submission_id uuid not null references public.submissions(id) on delete cascade,
  field_key text not null,             -- company_name, emails, urls, salary, payment ...
  field_value text not null
);

-- 3. findings: one row per matched warning sign
create table if not exists public.findings (
  id uuid primary key default gen_random_uuid(),
  submission_id uuid not null references public.submissions(id) on delete cascade,
  rule_id text,
  title text not null,
  severity text not null check (severity in ('strong', 'medium', 'weak', 'info')),
  matched_text text,
  source text,
  status text,
  confidence text,
  unverified text
);

-- 4. reports: your existing table, extended (existing rows keep working)
create table if not exists public.reports (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  risk_level text,
  input_text text,
  report jsonb not null
);
alter table public.reports add column if not exists submission_id uuid references public.submissions(id) on delete cascade;
alter table public.reports add column if not exists verdict text check (verdict in ('likely_fraudulent', 'suspicious', 'low_risk'));
alter table public.reports add column if not exists score int check (score between 0 and 100);
alter table public.reports add column if not exists mode text;
-- old rows may contain raw input_text. Uncomment to wipe it:
-- update public.reports set input_text = null;

-- 5. user_reports: community scam reports
create table if not exists public.user_reports (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  company_name text,
  recruiter_domain text,
  scam_type text not null,
  description text,
  ip_hash text,                        -- sha256 prefix, used only for rate limiting
  status text not null default 'new' check (status in ('new', 'reviewed', 'dismissed'))
);

-- indexes
create index if not exists reports_created_at_idx on public.reports (created_at desc);
create index if not exists reports_verdict_idx on public.reports (verdict);
create index if not exists findings_submission_idx on public.findings (submission_id);
create index if not exists fields_submission_idx on public.extracted_fields (submission_id);
create index if not exists user_reports_created_idx on public.user_reports (created_at desc);

-- ROW LEVEL SECURITY
-- The browser never talks to Supabase. Only the FastAPI backend does, using the
-- service_role key, which bypasses RLS. So: RLS on, NO policies, and no grants to
-- anon/authenticated. Anyone holding only the public anon key can read or write nothing.
alter table public.submissions       enable row level security;
alter table public.extracted_fields  enable row level security;
alter table public.findings          enable row level security;
alter table public.reports           enable row level security;
alter table public.user_reports      enable row level security;

revoke all on public.submissions, public.extracted_fields, public.findings,
              public.reports, public.user_reports from anon, authenticated;

-- OPTIONAL, later (public read-only aggregate for a public dashboard, never raw rows):
-- create view public.dashboard_verdicts with (security_invoker = false) as
--   select date_trunc('day', created_at) as day, verdict, count(*) as n
--   from public.reports group by 1, 2;
-- grant select on public.dashboard_verdicts to anon;

-- OPTIONAL: delete raw data older than 90 days (run from a Supabase cron job)
-- delete from public.submissions where created_at < now() - interval '90 days';
