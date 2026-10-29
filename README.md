# -OfferGuard-Evidence-Desk
OfferGuard does not claim to prove whether a job offer is genuine. It identifies explainable warning signals, checks available evidence, exposes missing verification, and helps job seekers decide what to confirm before taking action.
Features
Paste or upload: pasted text or text-based PDF offer letters (no OCR).
Field extraction: company name, recruiter emails, URLs, salary amounts, payment phrases.
10 deterministic, auditable rules (strong / medium / weak / info):
Upfront registration / processing / security fee
OTP, password, PIN or banking credential request
URL flagged by a reputation provider
Recruiter domain inconsistent with known company record
Personal email used for corporate hiring
Sensitive identity or banking documents requested early
Guaranteed selection or time pressure
Implausible salary for an entry-level role
Redirect to Telegram / WhatsApp / external form
Company or recruiter not independently verified
Evidence ledger: each finding shows claim, exact matched text with character offsets, source, check status, why it matters, uncertainty, next action.
Live URL reputation: Google Safe Browsing (optional key). "No known match" is never shown as "safe".
Company identity check: compares recruiter email domain with a small synthetic sample dataset (not an official registry).
Honest failure handling: unavailable or skipped checks are listed under "Not checked". A "Simulate URL check failure" toggle demos this.
Local fallback: if the backend is unreachable, the frontend runs a reduced rule set and labels it clearly.
Transparent risk indicator: rule-count level (high / elevated / some / none). Not a fraud probability.
Optional history: reports saved to Supabase when configured.
Tech stack
Layer	Tool
Frontend	React 18, Vite 5, plain CSS (light/dark)
Backend	Python, FastAPI, Pydantic, Uvicorn
PDF parsing	pypdf
HTTP client	httpx (async)
URL reputation	Google Safe Browsing API v4
Database (optional)	Supabase (Postgres via REST)
Tests	pytest + FastAPI TestClient
Hosting	Vercel (frontend and backend)
Project structure
offerguard/
├── frontend/              React + Vite app
│   └── src/
│       ├── App.jsx, api.js, styles.css, main.jsx
│       ├── report/        EvidenceLedger.jsx, FindingCard.jsx
│       └── fixtures/      demoCases.js (synthetic examples)
├── backend/               FastAPI app
│   ├── main.py            /health, /analyze, /analyze-pdf, /history
│   ├── schemas.py         request/response contract
│   ├── extract.py         field extraction + PDF text
│   ├── rules.py           deterministic rules (no network, no FastAPI)
│   ├── db.py              optional Supabase persistence
│   ├── checks/            url_reputation.py, company_identity.py
│   ├── fixtures/          company_records.json (synthetic)
│   ├── api/index.py       Vercel entrypoint
│   └── tests/             test_rules.py, test_analyze.py
└── supabase.sql           reports table
API
Method	Path	Description
GET	/health	{"status":"healthy"}
POST	/analyze	body {"text": "...", "simulate_url_failure": false} returns a report
POST	/analyze-pdf	multipart field file (text PDF, max 5MB)
GET	/history	saved reports if Supabase is configured

Report keys: extracted_fields, findings, checks, assessment, missing_checks, limitations, mode. Check statuses: verified_match, warning, no_match, unavailable, not_checked.

Run locally

Backend:

bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000

Open http://127.0.0.1:8000/docs

Frontend (new terminal):

bash
cd frontend
cp .env.example .env        # Windows: copy .env.example .env
npm install
npm run dev

Open http://localhost:5173

Tests: cd backend && python -m pytest -q

Environment variables

Backend (backend/.env.example):

FRONTEND_ORIGIN=https://your-app.vercel.app
SAFE_BROWSING_API_KEY=        # optional
SUPABASE_URL=                 # optional
SUPABASE_SERVICE_KEY=         # optional, keep server-side only

Frontend (frontend/.env.example):

VITE_API_BASE_URL=http://127.0.0.1:8000   # no trailing slash
Deploy (Vercel)
Backend project: root directory backend. Set env vars. Check /health.
Frontend project: root directory frontend, Vite preset. Set VITE_API_BASE_URL to the backend URL, then redeploy.
Set backend FRONTEND_ORIGIN to the frontend URL and redeploy the backend.
Optional: run supabase.sql in the Supabase SQL editor for history.
Limitations
Warning signals are not proof of fraud. No signals is not proof of safety.
A company-record match does not prove the recruiter is authorized.
Company data is a tiny synthetic sample, not an official registry (no live MCA lookup).
Scanned PDFs are not supported (no OCR).
Salary rule uses a fixed rule-of-thumb threshold, not market data.
Demo cases use fictional names only.
Roadmap
Live company registry integration
Evidence highlighting inside the original text
Verification checklist per report
Supabase Auth and per-user history
Optional LLM-assisted extraction (rules stay deterministic)
OCR for scanned PDFs, exportable PDF report
