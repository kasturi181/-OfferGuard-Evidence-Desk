# Deploy v2 without breaking the live site

Everything is additive, so the order below keeps the live app working at every step.

## 0. Secrets rules
- Secrets live only in **Render** and **Vercel** dashboards, and in local `.env` files (already in `.gitignore`).
- `SUPABASE_SERVICE_KEY`, `ANTHROPIC_API_KEY`, `OPENCORPORATES_API_TOKEN`, `SAFE_BROWSING_API_KEY`: **Render only**.
- The frontend gets one variable, `VITE_API_BASE_URL`. No Supabase key in the frontend. Anything with a `VITE_` prefix is public in the browser.
- If a key was ever pasted into chat, a commit or a screenshot, rotate it.
- Before committing run `git status` and check no `.env` is listed.

## 1. Database first (Supabase)
1. Supabase → SQL Editor → run `supabase_v3.sql`. Safe to re-run. Existing `reports` rows keep working (new columns are nullable).
2. Table Editor: confirm `submissions`, `extracted_fields`, `findings`, `reports`, `user_reports` show "RLS enabled" and have no policies.
3. Project Settings → API: copy **Project URL** and the **service_role** key (never the anon key into the backend).

## 2. Backend env (Render → service → Environment)
| Key | Value | Required |
|---|---|---|
| `SUPABASE_URL` | project URL | yes for storage |
| `SUPABASE_SERVICE_KEY` | service_role key | yes for storage |
| `FRONTEND_ORIGIN` | exact Vercel URL, no trailing slash. For preview URLs add them comma-separated only if your CORS code splits on commas | yes |
| `SAFE_BROWSING_API_KEY` | existing | optional |
| `OPENCORPORATES_API_TOKEN` | registry check | optional |
| `ANTHROPIC_API_KEY` | LLM extraction + explanation | optional |
| `STORE_INPUT_TEXT` | `false` (default) | optional |

No new Python packages. Build and start commands stay the same (typically `pip install -r requirements.txt` and `uvicorn main:app --host 0.0.0.0 --port $PORT`).

## 3. Ship the code
```bash
git checkout -b v2-verdict-dashboard
# copy files, apply the edits in INTEGRATION.md
cd backend && python -m pytest -q && cd ..
git add .
git status            # no .env!
git commit -m "Add verdict, evidence cards, dashboard, normalized Supabase storage"
git push -u origin v2-verdict-dashboard
```
- Vercel builds a **preview URL** for the branch. Preview talks to your live Render backend via `VITE_API_BASE_URL`. If CORS blocks it, add the preview origin to `FRONTEND_ORIGIN` or test locally.
- Render only deploys the branch it tracks (usually `main`). Merge the PR when the preview looks right.
- **Deploy order:** merge → Render finishes (watch Logs for "Application startup complete") → Vercel finishes. Old frontend + new backend works (extra fields ignored). New frontend + old backend would show empty panels, so backend first.

## 4. Verify live
1. `<render-url>/health` → `{"status":"healthy"}` (free tier sleeps, first hit ~50 s)
2. `<render-url>/docs` → see `/dashboard/stats`, `/dashboard/recent`, `/report-scam`
3. Analyze a demo text with a fee request → banner says "Likely fraudulent", Evidence card shows the matched text
4. Tick "Simulate URL check failure" → external checks show "Could not run", confidence drops, nothing says "safe"
5. Supabase Table Editor: new rows in `submissions`, `findings`, `reports`
6. Dashboard: "Sample data" badge disappears automatically once `reports` has rows
7. Submit a user report → row in `user_reports`

## 5. Replacing sample data with real data
- Nothing to change in the frontend. `/dashboard/stats` and `/dashboard/recent` return sample data only when Supabase is not configured or `reports` is empty.
- After a few real checks the badge disappears. To remove sample code entirely, delete `sample_stats`, `sample_recent` and the two `if not rows` branches in `routes_extra.py`.
- To seed demo rows for the judges, analyze 5-10 fictional offers from your demo cases on the live site.

## 6. Rollback
- Backend: Render → Events → roll back to the previous deploy. The new tables are unused by the old code, so no DB rollback is needed.
- Frontend: Vercel → Deployments → promote the previous one.
- DB: do not drop tables. To stop storing, empty `SUPABASE_SERVICE_KEY` on Render; the app keeps analysing.

## 7. Privacy notes for your README
- Raw text is not stored by default. Only a SHA-256 hash, length, extracted fields, findings and the report JSON are stored. The report JSON contains matched snippets, so treat `reports` as sensitive.
- User reports have emails and phone numbers stripped from the description before saving.
- Delete old data with the optional cron statement at the bottom of `supabase_v3.sql`.
- Add to README limitations: "Verdict is a rule-based risk assessment, not a legal determination. Registry check is a name search, not proof of authorization."
