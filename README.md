# OfferGuard Evidence Desk
Local run:
  cd backend && pip install -r requirements.txt && uvicorn main:app --reload   (port 8000)
  cd frontend && cp .env.example .env && npm i && npm run dev                  (port 5173)
Tests: cd backend && python -m pytest -q
Deploy: two Vercel projects (root dirs `backend` and `frontend`). Run supabase.sql in Supabase SQL editor for history.
Env backend: FRONTEND_ORIGIN, SAFE_BROWSING_API_KEY (opt), SUPABASE_URL, SUPABASE_SERVICE_KEY (opt)
Env frontend: VITE_API_BASE_URL
