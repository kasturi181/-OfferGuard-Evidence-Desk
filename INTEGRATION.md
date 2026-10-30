# Integration guide (v2)

Merge the `backend/` and `frontend/` folders from this zip into your repo (nothing existing is overwritten).
Edit only the 3 existing files listed below. Everything new is additive: old reports and old frontend keep working.

## Assumptions about your stack (correct me if wrong)

| Assumption | Used by |
|---|---|
| Backend: FastAPI app object named `app` in `backend/main.py`, run on Render with `uvicorn main:app` | router include |
| `/analyze` and `/analyze-pdf` build a report dict (or Pydantic model) with `extracted_fields`, `findings`, `checks`, `assessment`, `missing_checks`, `limitations`, `mode` (from your README) | `enrich_report` |
| Each finding has `severity` = `strong\|medium\|weak\|info` and ideally `title`, `matched_text`, `source`, `status` | verdict, cards |
| `extracted_fields` uses keys `company_name`, `emails`, `urls` (others optional: `location`, `registration_id`, `careers_domain`, `record_location`) | consistency |
| `report["assessment"]["level"]` is `high\|elevated\|some\|none` | dashboard column `risk_level` |
| Frontend: React + Vite, `src/main.jsx`, `src/App.jsx`, env `VITE_API_BASE_URL` | UI |
| `httpx` and `fastapi` already in `backend/requirements.txt` | no new packages |

## 1. Backend: 3 edits in `backend/main.py`

```python
# top of file
from routes_extra import router as extra_router
from enrich import enrich_report
from db_normalized import save_submission

# after app = FastAPI(...) and CORS setup
app.include_router(extra_router)
```

Inside `/analyze` (and the same in `/analyze-pdf`, with `source="pdf"`), after your existing code builds `report` and **before** returning:

```python
report = await enrich_report(report, text, simulate_failure=body.simulate_url_failure)
await save_submission(text, report, source="paste", simulate_failure=body.simulate_url_failure)
return report
```
- `text` = the pasted text or the text extracted from the PDF.
- If your response uses `response_model=...`, add these optional fields to the model in `schemas.py` (otherwise FastAPI strips them):
```python
consistency: list[dict] = []
checklist: list[dict] = []
guidance: dict | None = None
verdict: str | None = None
verdict_detail: dict | None = None
ai_explanation: str | None = None
```
- If your old code already saves to Supabase (`db.py`), remove that call so one analysis is not saved twice.
- `save_submission` never raises. If Supabase is down, the analysis still returns.

## 2. Frontend: 2 edits

`src/main.jsx` (after your existing css import):
```jsx
import "./styles_extra.css";
import "./styles_v2.css";
```

`src/App.jsx`:
```jsx
import { useState } from "react";
import NavTabs from "./components/NavTabs";
import ReportView from "./components/ReportView";
import Dashboard from "./pages/Dashboard";
import ReportScamForm from "./components/ReportScamForm";

// inside the component
const [page, setPage] = useState("check");

return (
  <>
    <NavTabs page={page} setPage={setPage} />
    <main className="og-page">
      {page === "check" && (<>
        {/* your existing input form (paste / PDF upload / simulate toggle) */}
        <ReportView report={report} />   {/* replaces your old EvidenceLedger render */}
      </>)}
      {page === "dashboard" && <Dashboard />}
      {page === "report" && <ReportScamForm />}
    </main>
  </>
);
```
Search the frontend for `genuine`, `safe`, `legit` and replace any claim. The new banner already says "Low risk: no strong warning signs found" with a disclaimer.

## 3. Optional switches (Render env)

| Var | Effect |
|---|---|
| `ANTHROPIC_API_KEY` | turns on LLM field extraction (fills missing fields only) and the plain-language explanation. Off = both skipped. |
| `ANTHROPIC_MODEL` | default `claude-sonnet-5-5` |
| `OPENCORPORATES_API_TOKEN` | turns on the registry check. Missing = shown as "Could not check", never "safe". |
| `STORE_INPUT_TEXT` | `true` stores redacted input text. Default `false` stores only a hash and length. |

## 4. Tests

```bash
cd backend && python -m pytest -q
```
`tests/test_new_modules.py` covers the verdict thresholds, determinism, honest-failure paths, LLM hallucination guard and redaction.

## 5. Where each deliverable lives

| # | Deliverable | Files |
|---|---|---|
| 1 | Features | `checklist.py`, `checks/consistency.py`, `checks/domain_age.py`, `checks/registry.py`, `guidance.py`, `llm_explain.py`, `enrich.py` |
| 2 | UI | `ReportView`, `VerdictBanner`, `EvidenceCard`, `ConsistencyPanel`, `ChecklistPanel`, `GuidancePanel`, `NavTabs`, `styles_v2.css` |
| 3 | Dashboard | `pages/Dashboard.jsx`, `routes_extra.py`, `db_extra.py` |
| 4 | Verdict | `verdict.py`, `VerdictBanner.jsx` |
| 5 | Supabase | `supabase_v3.sql`, `db_normalized.py`, `db_extra.py` |
| 6 | Deploy | `DEPLOY.md` |
