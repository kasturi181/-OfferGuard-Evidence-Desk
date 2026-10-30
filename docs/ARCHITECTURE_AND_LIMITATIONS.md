# OfferGuard Evidence Desk: Architecture, Tech Stack and Limitations

## 1. What it is
An explainable job-offer risk checker. The user pastes an offer (or uploads a text PDF or a screenshot). The system returns an evidence report: which warning signs were found, the exact words behind each, live lookup results, what could not be verified, and what to do next. It never claims an offer is genuine or fake, and it never says "safe".

## 2. System architecture
```
 Job seeker (browser)
   │ paste text / text PDF / screenshot
   ▼
 FRONTEND  React 18 + Vite   (hosted on Vercel)
   │  - screenshot → text with Tesseract.js, inside the browser (image never uploaded)
   │  - if backend is down → reduced local rules, clearly labelled
   │  POST /analyze  or  /analyze-pdf
   ▼
 BACKEND  FastAPI (Python 3.12)   (hosted on Render)
   1. Validate input (size limits) · PDF → text (pypdf)
   2. Extract fields: company, emails, links, CIN, salary, phones, cities (regex)
   3. Checks
        a) Cross-source: email domain, link domain, CIN, city vs company record (sample dataset)
        b) Live lookups, no API key: domain age (RDAP), DNS + mail records (DNS-over-HTTPS),
           redirect tracing (SSRF-guarded), look-alike domain patterns
        c) Offline CIN decoder (state, year, company type, internal contradictions)
        d) Google Safe Browsing (optional, only with key; otherwise "not checked")
   4. Rule engine: 19 deterministic rules → findings (strong / medium / weak / info)
   5. Assessment (rule-count level, not a probability) + checklist + ready-to-send messages
   ▼
 Evidence report (JSON) → shown with highlighted evidence, live-lookup cards, checklist
 Optional: Supabase Postgres (history, dashboard, scam reports). Not enabled in this deployment.
```

## 3. Tech stack
| Layer | Tool | Why |
|---|---|---|
| Frontend | React 18, Vite 5, plain CSS (light/dark) | Fast, small, no UI framework needed |
| OCR | Tesseract.js (in browser) | Screenshot text is read on the user's device |
| Backend | Python, FastAPI, Pydantic, Uvicorn | Typed request/response contract, auto docs at /docs |
| HTTP | httpx (async) | Parallel live lookups with timeouts |
| PDF | pypdf | Text-based PDFs |
| Live data | RDAP (rdap.org), Cloudflare DNS-over-HTTPS | Free, no API key |
| Optional data | Google Safe Browsing v4, Supabase (Postgres REST) | Coded, switched on by env vars |
| Tests | pytest, FastAPI TestClient (38 tests; network mocked) | Rules and live checks verified without internet |
| Hosting | Vercel (frontend), Render (backend), GitHub (CI by auto-deploy) | Free tiers |

## 4. Design decisions
- Deterministic rules, no LLM making decisions. The same input gives the same output, every finding points at exact text, and nothing is hallucinated.
- "Not checked" is never shown as "safe". Failed lookups are listed under "Not checked".
- Privacy: no account, offer text is not stored, screenshots never leave the device.
- Server-side redirect tracing refuses non-HTTP(S), IP literals, unusual ports and hosts resolving to non-public IPs, and never downloads page content.
- Evaluation tab: rules measured on 20 synthetic labelled messages (90% precision, 90% recall); the failures are shown.

## 5. Limitations (stated openly)
**Accuracy and meaning**
1. Warning signs are not proof of fraud. No warning signs is not proof of safety.
2. The risk level is a count of triggered rules, not a probability.
3. Rules cover common patterns only. New scam wording can be missed (the benchmark shows 1 miss and 1 false alarm).
4. The benchmark uses 20 synthetic messages we wrote. It does not measure real-world accuracy.
5. The salary rule uses a fixed rule-of-thumb limit (₹75,000/month for entry-level roles), not market data.
6. English-focused patterns. Hindi, Hinglish and other languages are only partly covered.

**Data and verification**
7. Company records are a tiny synthetic sample, not an official registry.
8. MCA has no public API. The CIN is decoded from its format only. It is NOT looked up, so a well-formed fake CIN passes the format check. Users must still verify on mca.gov.in.
9. A company-record match does not prove the recruiter is authorised.
10. Domain age comes from public registry data, which can be hidden, missing or wrong. A new domain can be a genuine startup, and an old domain can be hijacked.
11. Look-alike detection works from patterns and the company name in the text. It does not compare against a full list of brands.
12. Redirect tracing shows where a link goes, not whether the final page is malicious. Google Safe Browsing is optional and off without a key.
13. Community reports exist in the code but are off in this deployment.

**Input**
14. PDFs must contain text. Scanned PDFs need the screenshot upload instead.
15. Screenshot OCR can misread text, so users should check the text before analysing. OCR loads its language data from a CDN at first use.
16. Maximum 20,000 characters of text, 5 MB PDF, 8 MB image.

**Platform**
17. Free hosting: the Render server sleeps after about 15 minutes idle, so the first request can take 30 to 60 seconds. Live lookups add 5 to 15 seconds.
18. Live lookups depend on third-party services (rdap.org, Cloudflare). If they are down or rate-limited, the checks show "unavailable".
19. No user accounts and no saved history in this deployment. The Supabase code path is optional and not enabled.
20. No rate limiting or abuse protection beyond input size limits, so this is a demo-grade deployment.
21. Not legal advice and not an official fraud determination.

## 6. Why no sign-in or database in this version
Accounts and history add security duties (token checks, row-level security, data retention) and would add nothing to the core evidence feature. A privacy-first design that stores nothing was chosen. Optional Supabase history is implemented and can be enabled with environment variables (see README).

## 7. Future work
Official registry integration (MCA data licence), more languages, PDF evidence highlighting, user accounts with saved history, a browser extension, a shared community blocklist with moderation, rate limiting.
