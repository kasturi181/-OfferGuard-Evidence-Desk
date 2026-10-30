-- Real, well-known employers that scammers often impersonate. Safe to re-run (skips names already present).
-- With these rows OfferGuard can say "this recruiter email does NOT match the official domain of <company>".
--
-- IMPORTANT: I wrote these official domains from general knowledge. Before you submit, open each company's
-- own website and confirm the domain (2 minutes). Remove any row you are not sure about.
-- CIN and city are left empty on purpose so no wrong value can trigger a false mismatch.

insert into public.companies (name, official_domains, careers_url, source)
select v.name, v.official_domains, v.careers_url, 'official website (added manually, verify)'
from (values
  ('Tata Consultancy Services', array['tcs.com'],                     'https://www.tcs.com/careers'),
  ('Infosys',                   array['infosys.com'],                 'https://www.infosys.com/careers'),
  ('Wipro',                     array['wipro.com'],                   'https://careers.wipro.com'),
  ('HCL Technologies',          array['hcltech.com','hcl.com'],       'https://www.hcltech.com/careers'),
  ('Tech Mahindra',             array['techmahindra.com'],            'https://careers.techmahindra.com'),
  ('Cognizant',                 array['cognizant.com'],               'https://careers.cognizant.com'),
  ('Accenture',                 array['accenture.com'],               'https://www.accenture.com/in-en/careers'),
  ('Capgemini',                 array['capgemini.com'],               'https://www.capgemini.com/careers'),
  ('Amazon',                    array['amazon.com','amazon.in','amazon.jobs'], 'https://www.amazon.jobs'),
  ('Flipkart',                  array['flipkart.com'],                'https://www.flipkart.com'),
  ('Deloitte',                  array['deloitte.com'],                'https://www.deloitte.com'),
  ('Genpact',                   array['genpact.com'],                 'https://www.genpact.com/careers'),
  ('Zoho',                      array['zoho.com','zohocorp.com'],     'https://www.zoho.com/careers'),
  ('Mphasis',                   array['mphasis.com'],                 'https://www.mphasis.com/home/careers.html'),
  ('LTIMindtree',               array['ltimindtree.com'],             'https://www.ltimindtree.com/careers')
) as v(name, official_domains, careers_url)
where not exists (select 1 from public.companies c where lower(c.name) = lower(v.name));
