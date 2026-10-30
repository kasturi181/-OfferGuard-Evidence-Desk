import os

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import auth
import db
import learn
from checks.community import check_community
from checks.company_identity import check_company
from checks.url_reputation import check_urls
from extract import extract_fields, pdf_to_text
from benchmark import run_benchmark
from drafts import build_drafts
from explain import build_explanation
from guidance import build_checklist
from rules import LIMITS, assess, run_rules
from schemas import AnalyzeIn, Report, ReportIn

app = FastAPI(title="OfferGuard API")
origins = [o.strip() for o in os.getenv("FRONTEND_ORIGIN", "").split(",") if o.strip()] + ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_CHARS = 20000


async def analyze_text(text: str, simulate: bool = False, request: Request | None = None) -> dict:
    text = text.strip()
    if not text:
        raise HTTPException(422, "Empty input.")
    if len(text) > MAX_CHARS:
        raise HTTPException(413, f"Input too long (max {MAX_CHARS} chars).")
    fields = extract_fields(text)
    companies, source = await db.load_companies()
    checks = [await check_urls(fields["urls"], simulate), *check_company(text, fields, companies, source), await check_community(fields)]
    findings = run_rules(text, fields, checks)
    missing = [f"{c['name']}: {c['details']}" for c in checks if c["status"] in ("not_checked", "unavailable")]
    assessment = assess(findings)
    report = Report(extracted_fields=fields, findings=findings, checks=checks, assessment=assessment, missing_checks=missing,
                    limitations=LIMITS, checklist=build_checklist(findings), analyzed_text=text,
                    explain=build_explanation(findings, assessment), drafts=build_drafts(text, fields, findings, companies)).model_dump()
    user = await auth.current_user(request)
    await db.save_report_meta(report["assessment"]["level"], [f["rule_id"] for f in findings], fields["company"], user["id"] if user else None)
    if report["assessment"]["level"] == "high":  # learn recruiter details from strong scams so the next victim sees a match
        await db.insert_auto_signals(learn.signals_from(fields, findings, companies), auth.client_id(request, user))
    return report


@app.get("/")
def root():
    return {"service": "OfferGuard API", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    return {"status": "healthy", "database": db.enabled(), "login_required_for_reports": auth.login_required_for_reports()}


@app.post("/analyze")
async def analyze(body: AnalyzeIn, request: Request):
    return await analyze_text(body.text, body.simulate_url_failure, request)


@app.post("/analyze-pdf")
async def analyze_pdf(request: Request, file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > 5_000_000:
        raise HTTPException(413, "PDF too large (max 5MB).")
    try:
        text = pdf_to_text(data)
    except Exception:  # noqa: BLE001
        raise HTTPException(422, "Could not read PDF.")
    if len(text) < 20:
        raise HTTPException(422, "No extractable text. Scanned PDFs are not supported (no OCR). Paste the text instead.")
    return await analyze_text(text, False, request)


@app.post("/report")
async def report_scam(body: ReportIn, request: Request):
    if not db.enabled():
        raise HTTPException(503, "Reporting is not enabled (database not configured).")
    user = await auth.current_user(request)
    if auth.login_required_for_reports() and not user:
        raise HTTPException(401, "Please sign in to submit a report. Signing in keeps false and spam reports out.")
    who = auth.client_id(request, user)
    if not auth.rate_ok(who):
        raise HTTPException(429, "Too many reports from you in the last hour. Please try again later.")
    if not await db.insert_scam_report(body.kind, body.value, body.description, "user", who):
        raise HTTPException(502, "Could not save the report. Try again.")
    return {"saved": True, "message": "Thanks. Your report is stored as unverified."}


@app.get("/my-history")
async def my_history(request: Request):
    user = await auth.current_user(request)
    if not user:
        raise HTTPException(401, "Sign in to see your past checks.")
    try:
        rows = await db.list_reports(20, user["id"])
    except Exception:  # noqa: BLE001
        raise HTTPException(502, "Could not load your history. Has supabase_update.sql been run?")
    return {"email": user["email"], "items": rows or []}


@app.get("/benchmark")
def benchmark():
    return run_benchmark()


@app.get("/stats")
async def stats():
    return await db.stats()


@app.get("/history")
async def history():
    rows = await db.list_reports()
    if rows is None:
        return {"enabled": False, "items": []}
    return {"enabled": True, "items": rows}
