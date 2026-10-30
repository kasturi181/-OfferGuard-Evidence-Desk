-- OfferGuard update. Run ONCE in Supabase -> SQL Editor, AFTER supabase.sql. Safe to re-run.
-- Adds: auto-learned signals, per-person de-duplication, and per-user history (sign-in).
-- Do NOT run supabase_v3.sql (old, unused).

alter table public.scam_reports add column if not exists source text not null default 'user';   -- 'user' | 'auto'
alter table public.scam_reports add column if not exists reporter text;                          -- hashed id, never a raw IP
create unique index if not exists scam_reports_dedupe on public.scam_reports (kind, value, reporter);

alter table public.reports add column if not exists user_id uuid;                                -- set only for signed-in users
create index if not exists reports_user_idx on public.reports (user_id, created_at desc);

-- Same lock-down as before: only the backend (service-role key) can read or write.
alter table public.reports enable row level security;
alter table public.scam_reports enable row level security;
alter table public.companies enable row level security;
revoke all on public.reports, public.scam_reports, public.companies from anon, authenticated;
