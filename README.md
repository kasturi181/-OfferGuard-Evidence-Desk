# 🛡️ OfferGuard Evidence Desk

**Explainable job-offer risk checker.** Paste a recruitment message or upload a text PDF. Get an evidence-linked report: which warning signals were found, the exact text behind each one, what could not be verified, and what to do next.

> OfferGuard does not claim to prove whether a job offer is genuine. It identifies explainable warning signals, checks available evidence, exposes missing verification, and helps job seekers decide what to confirm before taking action.

🔗 **Live demo:** [EDIT: https://your-frontend.vercel.app](https://your-frontend.vercel.app)
⚙️ **API docs:** [EDIT: https://your-backend.vercel.app/docs](https://your-backend.vercel.app/docs)
🎥 **Demo video:** [EDIT: link, or delete this line]
🏆 **Built for:** [EDIT: FirstHack – Open Innovation track]
👤 **Author:** [EDIT: Your Name](https://github.com/kasturi181)

---

## Table of contents
1. [Problem](#problem)
2. [Solution](#solution)
3. [Features](#features)
4. [Screenshots](#screenshots)
5. [How it works](#how-it-works)
6. [Tech stack](#tech-stack)
7. [Project structure](#project-structure)
8. [API](#api)
9. [Run locally](#run-locally)
10. [Environment variables](#environment-variables)
11. [Deploy on Vercel](#deploy-on-vercel)
12. [Testing](#testing)
13. [Limitations](#limitations)
14. [Roadmap](#roadmap)
15. [Contributing](#contributing)
16. [License](#license)

---

## Problem
[EDIT: 2–3 lines. Example: Fake job offers that ask for registration fees, OTPs or personal documents target freshers every day. Job seekers have no quick way to check what is suspicious in a message or why.]

## Solution
OfferGuard turns one message or PDF into one traceable report. No black-box score. Every warning links to the exact text that triggered it, and every check that could not run is listed as "not checked", never as "safe".

## Features
- **Paste or upload**: pasted text or text-based PDF offer letters (no OCR).
- **Field extraction**: company name, recruiter emails, URLs, salary amounts, payment phrases.
- **10 deterministic, auditable rules** with strong / medium / weak / info severity:

| # | Rule | Severity |
|---|---|---|
| 1 | Upfront registration / processing / security fee | Strong |
| 2 | OTP, password, PIN or banking credential request | Strong |
| 3 | URL flagged by reputation provider | Strong |
| 4 | Recruiter domain inconsistent with known company record | Medium |
| 5 | Personal email used for corporate hiring | Medium |
| 6 | Sensitive identity / banking documents requested early | Medium |
| 7 | Guaranteed selection or time pressure | Medium |
| 8 | Implausible salary for an entry-level role | Medium |
| 9 | Redirect to Telegram / WhatsApp / external form | Weak |
| 10 | Company or recruiter not independently verified | Info |

- **Evidence ledger**: claim, exact matched text with character offsets, source, check status, why it matters, uncertainty, next action.
- **Live URL reputation** with Google Safe Browsing (optional key). "No known match" is never shown as "safe".
- **Company identity check** comparing recruiter email domain to a small synthetic sample dataset.
- **Honest failure handling**: unavailable checks are listed under "Not checked". A "Simulate URL check failure" toggle demonstrates this.
- **Local fallback**: if the backend is unreachable, the frontend runs a reduced rule set and labels it clearly.
- **Transparent risk indicator**: rule-count level (high / elevated / some / none). Not a fraud probability.
- **Optional history** saved to Supabase when configured.

## Screenshots
[EDIT: add images. Put files in a `docs/` folder, then use:]
```
![Report](docs/report.png)
![Not checked](docs/not-checked.png)
```

## How it works
```
User pastes text / uploads PDF
        │
        ▼
 Frontend (React + Vite) ──► POST /analyze ──► FastAPI
        │                                        │
        │                          extract fields (regex / pypdf)
        │                                        │
        │                     checks: Safe Browsing + company dataset
        │                                        │
        │                          rules engine (deterministic)
        │                                        │
        ◄──────────── evidence report (JSON) ────┘
        │
  backend down? ──► local fallback rules, clearly labelled
```

## Tech stack
| Layer | Tool |
|---|---|
| Frontend | React 18, Vite 5, plain CSS (light and dark) |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| PDF parsing | pypdf |
| HTTP client | httpx (async) |
| URL reputation | Google Safe Browsing API v4 |
| Database (optional) | Supabase (Postgres via REST) |
| Tests | pytest, FastAPI TestClient |
| Hosting | Vercel |

## Project structure
```
offerguard/
├── frontend/              React + Vite app
│   └── src/
│       ├── App.jsx, api.js, styles.css, main.jsx
│       ├── report/        EvidenceLedger.jsx, FindingCard.jsx
│       └── fixtures/      demoCases.js (synthetic examples)
├── backend/               FastAPI app
│   ├── main.py            /, /health, /analyze, /analyze-pdf, /history
│   ├── schemas.py         request / response contract
│   ├── extract.py         field extraction + PDF text
│   ├── rules.py           deterministic rules (no network, no FastAPI)
│   ├── db.py              optional Supabase persistence
│   ├── checks/            url_reputation.py, company_identity.py
│   ├── fixtures/          company_records.json (synthetic)
│   ├── api/index.py       Vercel entrypoint
│   └── tests/             test_rules.py, test_analyze.py
├── supabase.sql           reports table
└── README.md
```

## API
| Method | Path | Description |
|---|---|---|
| GET | `/health` | `{"status":"healthy"}` |
| POST | `/analyze` | body `{"text": "...", "simulate_url_failure": false}` returns a report |
| POST | `/analyze-pdf` | multipart field `file` (text PDF, max 5 MB) |
| GET | `/history` | saved reports if Supabase is configured |

Report keys: `extracted_fields`, `findings`, `checks`, `assessment`, `missing_checks`, `limitations`, `mode`.
Check statuses: `verified_match`, `warning`, `no_match`, `unavailable`, `not_checked`.

Example:
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Pay a refundable registration fee of Rs 2000 today."}'
```

## Run locally
**Backend**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
Open http://127.0.0.1:8000/docs

**Frontend** (new terminal)
```bash
cd frontend
copy .env.example .env            # macOS/Linux: cp .env.example .env
npm install
npm run dev
```
Open http://localhost:5173

## Environment variables
Backend (`backend/.env`):
```
FRONTEND_ORIGIN=https://your-frontend.vercel.app
SAFE_BROWSING_API_KEY=        # optional
SUPABASE_URL=                 # optional
SUPABASE_SERVICE_KEY=         # optional, server-side only, never in frontend
```
Frontend (`frontend/.env`):
```
VITE_API_BASE_URL=http://127.0.0.1:8000   # no trailing slash
```
Never commit `.env` files. Only `.env.example` is tracked.

## Deploy on Vercel
1. **Backend project**: import the repo, Root Directory `backend`, add env vars, deploy. Check `/health`.
2. **Frontend project**: import the repo, Root Directory `frontend`, Vite preset, set `VITE_API_BASE_URL` to the backend URL, deploy.
3. Set backend `FRONTEND_ORIGIN` to the frontend URL and redeploy the backend.
4. Optional: run `supabase.sql` in the Supabase SQL editor to enable history.

Changing a `VITE_` variable needs a redeploy of the frontend.

## Testing
```bash
cd backend
python -m pytest -q
```
Tests cover each rule, false-positive checks, input validation, bad PDFs and the unavailable-check path.

## Limitations
- Warning signals are not proof of fraud. No signals is not proof of safety.
- A company-record match does not prove the recruiter is authorized.
- Company data is a tiny synthetic sample, not an official registry (no live MCA lookup).
- Scanned PDFs are not supported (no OCR).
- Salary rule uses a fixed rule-of-thumb threshold, not market data.
- Demo cases use fictional names only.

## Roadmap
- [ ] Live company registry integration
- [ ] Highlight evidence inside the original text
- [ ] Per-report verification checklist
- [ ] Supabase Auth and per-user history
- [ ] Optional LLM-assisted extraction (rules stay deterministic)
- [ ] OCR for scanned PDFs
- [ ] Exportable PDF report
- [ ] [EDIT: your own idea]

## Contributing
1. Fork the repo and create a branch: `git checkout -b feature-name`
2. Add a test for any new rule in `backend/tests`
3. Run `python -m pytest -q`
4. Open a pull request

## License
[EDIT: MIT. Your GitHub repo already has a LICENSE file, so keep this line matching it.]

---
Disclaimer: OfferGuard is decision support, not legal advice. Verify any employer independently before paying or sharing documents.
