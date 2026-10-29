"""Extra routes: dashboard stats, recent checks, user scam reports.

In main.py add:
    from routes_extra import router as extra_router
    app.include_router(extra_router)
"""
from __future__ import annotations
import hashlib
import re
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

import db_extra as db

router = APIRouter()
_PII = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+|\+?\d[\d\s-]{7,}\d")
_hits: dict[str, deque] = defaultdict(deque)
LIMIT, WINDOW = 5, 3600  # 5 reports / hour / client (single instance; use Redis if you scale out)


def _client_hash(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    ip = (fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown"))
    return hashlib.sha256(ip.encode()).hexdigest()[:24]


def _limited(key: str) -> bool:
    now, q = time.time(), _hits[key]
    while q and now - q[0] > WINDOW:
        q.popleft()
    if len(q) >= LIMIT:
        return True
    q.append(now)
    return False


@router.get("/dashboard/stats")
async def dashboard_stats(days: int = Query(14, ge=3, le=60)):
    rows = await db.select("reports", {"select": "created_at,risk_level,verdict,report",
                                       "order": "created_at.desc", "limit": "500"})
    if not rows:  # None (not configured / error) or empty table -> sample, clearly labelled
        return db.sample_stats()
    out = db.summarize(rows, days)
    out["sample"] = False
    return out


@router.get("/dashboard/recent")
async def dashboard_recent(limit: int = Query(25, ge=1, le=100),
                           verdict: str | None = Query(None, pattern="^(likely_fraudulent|suspicious|low_risk)$")):
    params = {"select": "id,created_at,risk_level,verdict,report", "order": "created_at.desc", "limit": str(limit)}
    if verdict:
        params["verdict"] = f"eq.{verdict}"
    rows = await db.select("reports", params)
    if not rows:
        data = [r for r in db.sample_recent() if not verdict or r["verdict"] == verdict]
        return {"sample": True, "items": data}
    items = []
    for r in rows:
        rep = r.get("report") or {}
        findings = rep.get("findings") or []
        emails = (rep.get("extracted_fields") or {}).get("emails") or []
        items.append({
            "id": r["id"], "created_at": r["created_at"], "risk_level": r.get("risk_level"),
            "verdict": r.get("verdict"),
            "top_signal": db._finding_name(findings[0]) if findings else "No signals found",
            "domain": emails[0].rsplit("@", 1)[-1] if emails and "@" in emails[0] else ""})
    return {"sample": False, "items": items}


class UserReport(BaseModel):
    company_name: str = Field("", max_length=120)
    recruiter_domain: str = Field("", max_length=120)
    scam_type: str = Field(..., min_length=2, max_length=60)
    description: str = Field("", max_length=1000)


@router.post("/report-scam")
async def report_scam(body: UserReport, request: Request):
    key = _client_hash(request)
    if _limited(key):
        return {"saved": False, "message": "Too many reports from this connection. Try again later.",
                "official": {"portal": "https://cybercrime.gov.in", "helpline": "1930"}}
    ok = await db.insert("user_reports", {
        "company_name": body.company_name.strip(), "recruiter_domain": body.recruiter_domain.strip().lower(),
        "scam_type": body.scam_type.strip(), "description": _PII.sub("[removed]", body.description),
        "ip_hash": key})
    return {"saved": ok,
            "message": "Thanks. Report saved." if ok else
            "Database not connected. Report not saved. Please also report at cybercrime.gov.in or call 1930.",
            "official": {"portal": "https://cybercrime.gov.in", "helpline": "1930"}}
