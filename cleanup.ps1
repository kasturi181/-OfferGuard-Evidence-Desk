# Removes files from my earlier zips that landed in the wrong place or are unused. Run from the repo root.
# Review with:  git status   (nothing important is deleted; everything is in git history)
git rm -r --ignore-unmatch checks fixtures tests `
  frontend/components frontend/pages frontend/api_extra.js frontend/styles_extra.css frontend/styles_v2.css `
  DEPLOY.md INTEGRATION.md supabase_v3.sql `
  backend/checklist.py backend/db_extra.py backend/db_normalized.py backend/enrich.py backend/llm_explain.py `
  backend/routes_extra.py backend/verdict.py backend/.env.example.additions `
  backend/checks/consistency.py backend/checks/domain_age.py backend/checks/registry.py backend/tests/test_new_modules.py
Write-Host "Cleanup staged. Now run: git status"
