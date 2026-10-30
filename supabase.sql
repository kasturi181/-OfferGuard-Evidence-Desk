-- OfferGuard schema. Run once in Supabase -> SQL Editor. Safe to re-run.

-- 1) Analysis metadata (NO offer text is stored, only the outcome)
create table if not exists public.reports (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  risk_level text,
  rule_ids text[] default '{}',
  company text
);
alter table public.reports add column if not exists rule_ids text[] default '{}';
alter table public.reports add column if not exists company text;
do $$ begin
  if exists (select 1 from information_schema.columns where table_schema='public' and table_name='reports' and column_name='input_text') then
    alter table public.reports alter column input_text drop not null;
  end if;
  if exists (select 1 from information_schema.columns where table_schema='public' and table_name='reports' and column_name='report') then
    alter table public.reports alter column report drop not null;
  end if;
end $$;

-- 2) Curated list of GENUINE companies and their official details (add your own rows here)
create table if not exists public.companies (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  official_domains text[] not null default '{}',
  cin text,
  city text,
  careers_url text,
  source text,
  verified_at date default current_date
);

-- 3) User-submitted scam reports (unverified)
create table if not exists public.scam_reports (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  kind text not null check (kind in ('email','domain','company','phone')),
  value text not null,
  description text,
  status text not null default 'unverified'
);
create index if not exists scam_reports_value_idx on public.scam_reports (value);

-- Only the backend (service-role key) can read/write. No public policies.
alter table public.reports enable row level security;
alter table public.companies enable row level security;
alter table public.scam_reports enable row level security;

-- Synthetic demo rows (delete or replace with real, verified data)
insert into public.companies (name, official_domains, cin, city, careers_url, source)
select * from (values
  ('Northwind Tech Pvt Ltd', array['northwindtech.example'], 'U72900KA2015PTC123456', 'Bengaluru', 'https://northwindtech.example/careers', 'synthetic demo'),
  ('Contoso Analytics Limited', array['contosoanalytics.example'], 'U74999MH2012PLC234567', 'Mumbai', 'https://contosoanalytics.example/careers', 'synthetic demo'),
  ('Fabrikam Systems Pvt Ltd', array['fabrikamsystems.example'], 'U72200TG2018PTC345678', 'Hyderabad', 'https://fabrikamsystems.example/jobs', 'synthetic demo')
) as v(name, official_domains, cin, city, careers_url, source)
where not exists (select 1 from public.companies);

insert into public.scam_reports (kind, value, description)
select * from (values
  ('email', 'payments@fake-hiring.example', 'Synthetic demo: asked for a registration fee'),
  ('domain', 'northwind-careers.com', 'Synthetic demo: look-alike of a real company domain'),
  ('phone', '9000000001', 'Synthetic demo: WhatsApp recruiter asking for OTP')
) as v(kind, value, description)
where not exists (select 1 from public.scam_reports);
