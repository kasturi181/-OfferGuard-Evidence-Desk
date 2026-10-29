"""Supabase REST helpers for dashboard + user reports. Server-side only.

Uses SUPABASE_URL and SUPABASE_SERVICE_KEY. If not set (or table empty),
dashboard routes return clearly labelled SAMPLE data. Delete sample_* later
when real data is flowing (see DEPLOY.md).
"""
from __future__ import annotations
import os
from collections import Counter
from datetime import datetime, timedelta, timezone

TIMEOUT = 8.0


def configured() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY"))


def _headers(extra=None):
    key = os.environ["SUPABASE_SERVICE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    h.update(extra or {})
    return h


def _url(table: str) -> str:
    return os.environ["SUPABASE_URL"].rstrip("/") + f"/rest/v1/{table}"


async def select(table: str, params: dict) -> list[dict] | None:
    if not configured():
        return None
    import httpx
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.get(_url(table), headers=_headers(), params=params)
            r.raise_for_status()
            return r.json()
    except Exception:
        return None


async def insert(table: str, row: dict) -> bool:
    if not configured():
        return False
    import httpx
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.post(_url(table), headers=_headers({"Prefer": "return=minimal"}), json=row)
            r.raise_for_status()
            return True
    except Exception:
        return False


def _finding_name(f) -> str:
    if isinstance(f, dict):
        return str(f.get("title") or f.get("rule") or f.get("id") or f.get("claim") or "unknown")
    return str(f)


def summarize(rows: list[dict], days: int = 14) -> dict:
    levels = Counter((r.get("risk_level") or "none") for r in rows)
    verdicts = Counter((r.get("verdict") or "unknown") for r in rows)
    rules = Counter()
    unverified = 0
    for r in rows:
        rep = r.get("report") or {}
        for f in rep.get("findings", []) or []:
            rules[_finding_name(f)] += 1
        if rep.get("missing_checks"):
            unverified += 1
    today = datetime.now(timezone.utc).date()
    per_day = Counter()
    for r in rows:
        try:
            per_day[datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")).date()] += 1
        except Exception:
            pass
    series = [{"date": (today - timedelta(days=i)).isoformat(),
               "count": per_day.get(today - timedelta(days=i), 0)} for i in range(days - 1, -1, -1)]
    return {
        "total": len(rows),
        "high": levels.get("high", 0), "elevated": levels.get("elevated", 0),
        "some": levels.get("some", 0), "none": levels.get("none", 0),
        "verdicts": {"likely_fraudulent": verdicts.get("likely_fraudulent", 0),
                     "suspicious": verdicts.get("suspicious", 0),
                     "low_risk": verdicts.get("low_risk", 0)},
        "with_unverified": unverified,
        "top_rules": [{"rule": k, "count": v} for k, v in rules.most_common(8)],
        "per_day": series,
    }


SAMPLE_NOTE = "Sample data (fictional). Real records replace it automatically once checks are saved."


def sample_stats() -> dict:
    today = datetime.now(timezone.utc).date()
    counts = [3, 5, 4, 8, 6, 9, 7, 11, 8, 12, 10, 9, 14, 13]
    return {
        "sample": True, "note": SAMPLE_NOTE,
        "total": 112, "high": 31, "elevated": 27, "some": 22, "none": 32,
        "verdicts": {"likely_fraudulent": 38, "suspicious": 29, "low_risk": 45},
        "with_unverified": 96,
        "top_rules": [
            {"rule": "Upfront registration / processing fee", "count": 31},
            {"rule": "Redirect to Telegram / WhatsApp", "count": 27},
            {"rule": "Personal email for corporate hiring", "count": 24},
            {"rule": "Company not independently verified", "count": 22},
            {"rule": "Guaranteed selection / time pressure", "count": 15},
            {"rule": "OTP / credential request", "count": 9}],
        "per_day": [{"date": (today - timedelta(days=13 - i)).isoformat(), "count": c}
                    for i, c in enumerate(counts)],
    }


def sample_recent() -> list[dict]:
    now = datetime.now(timezone.utc)
    items = [("high", "likely_fraudulent", "Upfront registration / processing fee", "talentdesk-hr.example"),
             ("elevated", "suspicious", "Personal email for corporate hiring", "gmail.com"),
             ("some", "suspicious", "Company not independently verified", "northwind-demo.example"),
             ("high", "likely_fraudulent", "OTP / credential request", "careers-apply.example"),
             ("none", "low_risk", "No signals found", "acme-demo.example")]
    return [{"id": f"sample-{i}", "created_at": (now - timedelta(hours=i * 7)).isoformat(),
             "risk_level": lvl, "verdict": ver, "top_signal": sig, "domain": dom}
            for i, (lvl, ver, sig, dom) in enumerate(items)]
