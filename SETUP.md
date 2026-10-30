# Final setup (about 45 minutes)

Do the steps in order. Each one has a check so you know it worked.

## 1. Apply the files (5 min)
Unzip `offerguard-final.zip` into the repo root (the folder that contains `backend` and `frontend`), choose **Replace**. Then, in PowerShell from the repo root:
```powershell
.\cleanup.ps1
cd frontend
npm install          # adds @supabase/supabase-js and updates package-lock.json
npm run build        # must finish with "built in"
cd ..\backend
python -m pytest -q  # should pass
cd ..
```

## 2. Supabase database (5 min)
Supabase dashboard -> SQL Editor -> run these, one at a time, in this order:
1. `supabase.sql` (skip if you already ran it)
2. `supabase_update.sql`
3. `supabase_seed_companies.sql`  (first open each company's website and confirm the domain; delete rows you are unsure about)

Do NOT run `supabase_v3.sql`.

## 3. Supabase keys (2 min)
Project Settings -> API. You need three things:
- **Project URL**
- **service_role** key: SECRET. Backend only.
- **anon public** key: public. Frontend.

## 4. Supabase sign-in (3 min)
Authentication -> Sign In / Providers -> **Email** is on (magic link).
Authentication -> URL Configuration:
- Site URL = your frontend URL (e.g. `https://offerguard-xxxx.vercel.app`)
- Redirect URLs = add the same URL.

Note: Supabase's built-in email sender allows only a few sign-in emails per hour. Sign in once before your demo and stay signed in.

## 5. Render backend variables (3 min)
Render -> your backend service -> Environment:

| Key | Value |
|---|---|
| SUPABASE_URL | Project URL |
| SUPABASE_SERVICE_KEY | service_role key |
| FRONTEND_ORIGIN | your frontend URL, no trailing slash |
| SAFE_BROWSING_API_KEY | see below |
| REQUIRE_LOGIN_FOR_REPORTS | `true` to force sign-in for reports (optional) |

Safe Browsing key (free): console.cloud.google.com -> new project -> APIs & Services -> Library -> enable **Safe Browsing API** -> Credentials -> Create API key.

Save. Render redeploys.

## 6. Vercel frontend variables (3 min)
Vercel -> project -> Settings -> Environment Variables. Tick **Production** (and Preview):
- `VITE_API_BASE_URL` = your Render URL (no trailing slash)
- `VITE_SUPABASE_URL` = Project URL
- `VITE_SUPABASE_ANON_KEY` = anon key

## 7. Push and deploy (5 min)
```powershell
git add .
git status          # make sure there is no .env file
git commit -m "Verify links, auto-learned signals, sign-in, real companies"
git push
```
Then merge to `main` (Pull request -> Merge). Vercel Production builds from `main`. In Render, check Settings -> Branch is the branch you want live.

## 8. Check it works (10 min)
1. `<render-url>/health` shows `"database": true`.
2. Open the site. Header shows **Sign in**. Dashboard no longer says "Database not connected".
3. Paste: `Selected at Infosys. Pay a refundable registration fee of Rs 2500. Contact hr.jobs@gmail.com` -> High concern, "Personal email" and a company match, plus the **Verify it yourself** panel with working links.
4. Report tab -> report phone `9000000009` -> analyze a text containing that number -> Matches reports appears.
5. Sign in -> **My checks** tab lists your analysis.
6. If something fails: Render -> Logs. Paste the last 20 lines to me.

## How the community signal works (for your pitch)
- A user report counts right away (one per person per detail).
- When a check finds a fee or OTP request, the recruiter's email, domain and phone are remembered.
- An auto-remembered detail is shown only after 2 different people hit it. 3 or more matches raise the signal from weak to medium.
- Big sites (LinkedIn, Google, shorteners) and verified company domains are never learned, so nobody can smear a real company.
- It is always labelled unverified, and it never becomes a verdict by itself.

## Still yours to fill in (README)
Live demo URL, demo video link, event name, screenshots.
