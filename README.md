# 🛡️ OfferGuard Evidence Desk

**Explainable job-offer risk checker.** Paste a recruitment message or upload a text PDF. Get an evidence-linked report: which warning signals were found, the exact text behind each one, what could not be verified, and what to do next.

> OfferGuard does not claim to prove whether a job offer is genuine. It identifies explainable warning signals, checks available evidence, exposes missing verification, and helps job seekers decide what to confirm before taking action.

🔗 **Live demo:** [EDIT: https://your-frontend.vercel.app](https://your-frontend.vercel.app)
⚙️ **API docs:** [offerguard-api-20f2.onrender.com/docs](https://offerguard-api-20f2.onrender.com/docs) (free hosting: the first request can take about a minute to wake the server)
🎥 **Demo video:** [EDIT: link, or delete this line]
🏆 **Built for:** [EDIT: FirstHack – Open Innovation track]
👤 **Author:** [Kasturi Adakure](https://github.com/kasturi181)

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
11. [Deploy](#deploy)
12. [Testing](#testing)
13. [Limitations](#limitations)
14. [Roadmap](#roadmap)
15. [Contributing](#contributing)
16. [License](#license)

---

## Problem
Fake job offers that ask for registration fees, OTPs or identity documents target freshers every day. Checking one by hand means 15 minutes of searching the company, the recruiter's email, the website and the phone number. Most people skip it, or do not know what to look for.

OfferGuard does that first pass in seconds, shows exactly which words raised a flag, and gives one-click links for the checks no software can do for you.

## Solution
OfferGuard turns one message or PDF into one traceable report. No black-box score. Every warning links to the exact text that triggered it, and every check that could not run is listed as "not checked", never as "safe".

## Features
- **Paste, PDF or screenshot**: paste text, upload a text PDF, or upload a screenshot of a chat. Screenshots are read on the user's device with OCR (tesseract.js); the image is never uploaded.
- **Verify it yourself in 60 seconds**: for every company, website, email and phone number found, one-click searches (scam reports, Safe Browsing status, WHOIS, MCA, LinkedIn, Truecaller) so users do not have to research from scratch.
- **Community signal that grows with use**: user reports plus recruiter details auto-remembered from strong scams (fee or OTP requests). A match is shown only as an unverified signal, and an auto-learned one needs 2 different reporters. Well-known sites and verified company domains are never learned.
- **Optional sign-in** (Supabase magic link): personal history of past checks (outcome only, never the offer text) and spam protection for reports.
- **Field extraction**: company name, recruiter emails, URLs, salary amounts, payment phrases.
- **Offer brief** at the top of every report: what the offer says (role, company, place, start date, pay), whether to proceed (do not proceed / pause / verify first), what you risk if you go ahead unverified, and what to confirm first. Missing details are shown as "Not stated", never guessed.
- **Website details**: registration date and age of every website or company email domain in the message (public RDAP data). A very new site is a weak signal.
- **Audit trail** on every report: all 15 rules shown as triggered, clear, or could not run; every check with its source; how the result was made; downloadable as JSON.
- **15 deterministic, auditable rules** with strong / medium / weak / info severity:

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
| 11 | Link in offer points away from the company's official domain | Medium |
| 12 | Registration ID (CIN) differs from the record | Medium |
| 13 | Offer location differs from the recorded office | Weak |
| 14 | Details match unverified user reports or earlier high-risk checks | Weak (Medium when 3 or more match) |
| 15 | Website in the offer was registered less than 90 days ago | Weak |

- **Evidence ledger**: claim, exact matched text with character offsets, source, check status, why it matters, uncertainty, next action.
- **Live URL reputation** with Google Safe Browsing (optional key). "No known match" is never shown as "safe".
- **Company identity check** comparing recruiter email and link domains to a curated list of employers (a `companies` table you can extend; includes well-known brands that scammers impersonate).
- **Honest failure handling**: unavailable checks are listed under "Not checked". A "Simulate URL check failure" toggle demonstrates this.
- **Local fallback**: if the backend is unreachable, the frontend runs a reduced rule set and labels it clearly.
- **Transparent risk indicator**: rule-count level (high / elevated / some / none). Not a fraud probability.
- **Cross-source consistency**: email domain, link domains, CIN and location are each compared with the company record and explained individually.
- **Tailored safety checklist**: next steps matched to the signals found (cybercrime.gov.in, 1930, MCA lookup).
- **Evidence highlighted inside your original message.**
- **Plain-language summary in English and हिन्दी** (deterministic, no LLM), so job seekers can read the result in their own language.
- **Ready-to-send verification messages**: a message to the recruiter, one to the company's official HR, and notes for a cybercrime report, all filled from what was found.
- **Evaluation tab**: the rules are measured on 20 synthetic, manually labelled messages (precision, recall, and every failure shown openly).
- **Save report as PDF** (print-friendly layout).
- **Dashboard** (aggregate stats, no offer text stored) and **Report a scam** (unverified, masked user reports) backed by Supabase.
- **Curated company list** in the Supabase `companies` table, with a local fixture fallback.

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
| POST | `/report` | submit an unverified scam report `{kind, value, description}` |
| GET | `/stats` | dashboard aggregates |
| GET | `/benchmark` | rule evaluation on 20 synthetic labelled messages |
| GET | `/history` | saved analysis metadata if Supabase is configured |

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

## Deploy
- **Backend**: Render Web Service. Root Directory `backend`, build `pip install -r requirements.txt`, start `uvicorn main:app --host 0.0.0.0 --port $PORT`. Check `/health`.
- **Frontend**: Vercel (or a Render Static Site). Root Directory `frontend`, Vite preset, set `VITE_API_BASE_URL` to the backend URL.
- Set backend `FRONTEND_ORIGIN` to the frontend URL.
- **Database**: in the Supabase SQL editor run `supabase.sql`, then `supabase_update.sql`, then (after checking each domain) `supabase_seed_companies.sql`.
- **Sign-in (optional)**: set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` on the frontend. Only the public anon key goes in the frontend; the service key stays on the backend.
- Changing a `VITE_` variable needs a redeploy of the frontend.

## Testing
```bash
cd backend
python -m pytest -q
```
Tests cover each rule, false-positive checks, input validation, bad PDFs and the unavailable-check path.

## Evaluation
Offline test on 20 hand-labelled synthetic messages (10 scam, 10 normal), run from the Evaluation tab: 18 correct, precision 0.90, recall 0.90. One scam was missed (a UPI payment phrased as a uniform fee) and one normal message was flagged (a real founder using a Gmail address). This measures the rules on examples we wrote, not real-world accuracy.

## Use of AI
- **Decisions are rule-based on purpose.** Every flag is auditable and links to the exact words. No generative AI or language model decides the result, writes the explanations (fixed English and Hindi templates) or scores the offer.
- **Machine learning is used for one thing:** reading screenshots with Tesseract OCR, which runs on the user's device.
- **Built with an AI coding assistant** (Claude), then reviewed and tested by the author.
- **Possible future use:** a language model could extract details from messy or regional-language messages and explain results in more languages. It would never set the verdict, and every extracted value would have to appear in the original text.

## Limitations
- Warning signals are not proof of fraud. No signals is not proof of safety.
- A company-record match does not prove the recruiter is authorized.
- Company data is a curated list, not an official registry (no live MCA lookup). Unknown companies show as "not checked".
- Scanned PDFs are not read directly; upload a screenshot of the page instead. OCR can misread characters, so check the extracted text.
- Community signals depend on how many people use the tool, and reports are unverified.
- A rule-based tool cannot prove an offer is genuine. A clean result means "no known warning signs", so verify the employer yourself.
- Salary rule uses a fixed rule-of-thumb threshold, not market data.
- Demo cases use fictional names only.

## Roadmap
- [x] Highlight evidence inside the original text
- [x] Per-report verification checklist and one-click verify links
- [x] Screenshot OCR
- [x] Supabase Auth and per-user history
- [x] Auto-learned community signal
- [x] Exportable PDF report (print to PDF)
- [ ] Live company registry integration (MCA)
- [ ] OCR for scanned multi-page PDFs
- [ ] Optional LLM-assisted extraction (rules stay deterministic)
- [ ] Moderator review of community reports

## Contributing
1. Fork the repo and create a branch: `git checkout -b feature-name`
2. Add a test for any new rule in `backend/tests`
3. Run `python -m pytest -q`
4. Open a pull request

## License
MIT. See [LICENSE](LICENSE).

---
Disclaimer: OfferGuard is decision support, not legal advice. Verify any employer independently before paying or sharing documents.
