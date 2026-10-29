import os
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
 
import db
from checks.company_identity import check_company
from checks.url_reputation import check_urls
from extract import extract_fields, pdf_to_text
from rules import LIMITS, assess, run_rules
from schemas import AnalyzeIn, Report
 
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
 
 
async def analyze_text(text: str, simulate: bool = False) -> dict:
    text = text.strip()
    if not text:
        raise HTTPException(422, "Empty input.")
    if len(text) > MAX_CHARS:
        raise HTTPException(413, f"Input too long (max {MAX_CHARS} chars).")
    fields = extract_fields(text)
    checks = [await check_urls(fields["urls"], simulate), check_company(text, fields)]
    findings = run_rules(text, fields, checks)
    missing = [f"{c['name']}: {c['details']}" for c in checks if c["status"] in ("not_checked", "unavailable")]
    report = Report(extracted_fields=fields, findings=findings, checks=checks, assessment=assess(findings),
                    missing_checks=missing, limitations=LIMITS).model_dump()
    await db.save_report(text, report)
    return report
 
 
@app.get("/")
def root():
    return {"service": "OfferGuard API", "docs": "/docs", "health": "/health"}
 
 
@app.get("/health")
def health():
    return {"status": "healthy"}
 
 
@app.post("/analyze")
async def analyze(body: AnalyzeIn):
    return await analyze_text(body.text, body.simulate_url_failure)
 
 
@app.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > 5_000_000:
        raise HTTPException(413, "PDF too large (max 5MB).")
    try:
        text = pdf_to_text(data)
    except Exception:  # noqa: BLE001
        raise HTTPException(422, "Could not read PDF.")
    if len(text) < 20:
        raise HTTPException(422, "No extractable text. Scanned PDFs are not supported (no OCR). Paste the text instead.")
    return await analyze_text(text)
 
 
@app.get("/history")
async def history():
    rows = await db.list_reports()
    if rows is None:
        return {"enabled": False, "items": []}
    return {"enabled": True, "items": rows}
 
