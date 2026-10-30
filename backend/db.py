"""Supabase over REST. Everything degrades gracefully when env vars are missing."""
import json
import os
import re
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

FIXTURE = Path(__file__).parent / "fixtures" / "company_records.json"
_cache = {"t": 0.0, "rows": None}
KINDS = ("email", "domain", "company", "phone")


def _cfg():
    u, k = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY")
    if not (u and k):
        return None
    return u.rstrip("/"), {"apikey": k, "Authorization": f"Bearer {k}", "Content-Type": "application/json"}


def enabled() -> bool:
    return _cfg() is not None


def fixture_companies() -> list[dict]:
    return json.loads(FIXTURE.read_text())["records"]


async def load_companies():
    """Returns (rows, source_label)."""
    cfg = _cfg()
    if not cfg:
        return fixture_companies(), "Synthetic sample dataset (NOT an official registry)"
    if _cache["rows"] is not None and time.time() - _cache["t"] < 60:
        return _cache["rows"], "Supabase `companies` table (curated, NOT an official registry)"
    url, h = cfg
    try:
        async with httpx.AsyncClient(timeout=3.0) as c:
            r = await c.get(f"{url}/rest/v1/companies", headers=h, params={"select": "name,official_domains,cin,city,careers_url,source"})
            r.raise_for_status()
            rows = r.json()
        if rows:
            _cache.update(t=time.time(), rows=rows)
            return rows, "Supabase `companies` table (curated, NOT an official registry)"
    except Exception:  # noqa: BLE001
        pass
    return fixture_companies(), "Synthetic sample dataset (NOT an official registry)"


def clean(v: str) -> str:
    return re.sub(r"[,()\"'\\]", "", v.strip().lower())[:200]


async def find_scam_reports(values: list[str]):
    """Returns (status, rows). status: disabled | error | ok"""
    cfg = _cfg()
    if not cfg:
        return "disabled", []
    if not values:
        return "ok", []
    url, h = cfg
    try:
        async with httpx.AsyncClient(timeout=3.0) as c:
            r = await c.get(f"{url}/rest/v1/scam_reports", headers=h,
                            params={"select": "*", "value": "in.(" + ",".join(clean(v) for v in values) + ")", "limit": "300"})
            r.raise_for_status()
            return "ok", r.json()
    except Exception:  # noqa: BLE001
        return "error", []


async def insert_scam_report(kind: str, value: str, description: str, source: str = "user", reporter: str | None = None) -> bool:
    """One row per (kind, value, reporter): the same person reporting twice does not inflate the count.
    Falls back to the old column set if the migration (supabase_update.sql) has not been run yet."""
    cfg = _cfg()
    if not cfg:
        return False
    url, h = cfg
    row = {"kind": kind, "value": clean(value), "description": description[:500], "source": source, "reporter": reporter}
    try:
        async with httpx.AsyncClient(timeout=4.0) as c:
            r = await c.post(f"{url}/rest/v1/scam_reports", params={"on_conflict": "kind,value,reporter"},
                             headers={**h, "Prefer": "resolution=ignore-duplicates,return=minimal"}, json=row)
            if r.status_code < 300:
                return True
            legacy = await c.post(f"{url}/rest/v1/scam_reports", headers=h, json={"kind": kind, "value": clean(value), "description": description[:500]})
            return legacy.status_code < 300
    except Exception:  # noqa: BLE001
        return False


async def insert_auto_signals(items: list[tuple[str, str]], reporter: str) -> bool:
    """Remember recruiter details seen in a high-risk analysis. Silent on failure; never blocks the analysis."""
    cfg = _cfg()
    if not (cfg and items):
        return False
    url, h = cfg
    rows = [{"kind": k, "value": clean(v), "description": "Auto: seen in a high-risk analysis", "source": "auto", "reporter": reporter} for k, v in items]
    try:
        async with httpx.AsyncClient(timeout=4.0) as c:
            r = await c.post(f"{url}/rest/v1/scam_reports", params={"on_conflict": "kind,value,reporter"},
                             headers={**h, "Prefer": "resolution=ignore-duplicates,return=minimal"}, json=rows)
            return r.status_code < 300
    except Exception:  # noqa: BLE001
        return False


async def save_report_meta(level: str, rule_ids: list[str], company: str | None, user_id: str | None = None) -> bool:
    """Stores only metadata, never the offer text (privacy). user_id is set only when the user is signed in."""
    cfg = _cfg()
    if not cfg:
        return False
    url, h = cfg
    row = {"risk_level": level, "rule_ids": rule_ids, "company": company}
    try:
        async with httpx.AsyncClient(timeout=3.0) as c:
            if user_id:
                r = await c.post(f"{url}/rest/v1/reports", headers=h, json={**row, "user_id": user_id})
                if r.status_code < 300:
                    return True
            r = await c.post(f"{url}/rest/v1/reports", headers=h, json=row)
            return r.status_code < 300
    except Exception:  # noqa: BLE001
        return False


def mask(kind: str, value: str) -> str:
    if "@" in value:
        local, dom = value.split("@", 1)
        return local[:2] + "***@" + dom
    if kind == "phone":
        return "******" + value[-3:]
    return value if kind == "domain" else value[:3] + "***"


async def stats() -> dict:
    cfg = _cfg()
    companies = len((await load_companies())[0])
    if not cfg:
        return {"enabled": False, "companies_in_dataset": companies}
    url, h = cfg
    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            rr = await c.get(f"{url}/rest/v1/reports", headers=h, params={"select": "created_at,risk_level,rule_ids", "order": "created_at.desc", "limit": "1000"})
            sr = await c.get(f"{url}/rest/v1/scam_reports", headers=h, params={"select": "*", "order": "created_at.desc", "limit": "500"})
            rr.raise_for_status(); sr.raise_for_status()
            reps, scams = rr.json(), [x for x in sr.json() if x.get("source") != "auto"]
    except Exception:  # noqa: BLE001
        return {"enabled": False, "companies_in_dataset": companies, "error": "database unreachable"}
    levels = Counter(r["risk_level"] for r in reps)
    rules = Counter(x for r in reps for x in (r.get("rule_ids") or []))
    today = datetime.now(timezone.utc).date()
    days = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    per_day = Counter(r["created_at"][:10] for r in reps)
    return {
        "enabled": True, "companies_in_dataset": companies, "total_analyses": len(reps),
        "by_level": {k: levels.get(k, 0) for k in ("high", "elevated", "some", "none")},
        "top_rules": [{"rule_id": k, "count": v} for k, v in rules.most_common(6)],
        "daily": [{"date": d, "count": per_day.get(d, 0)} for d in days],
        "scam_reports": {"total": len(scams), "by_kind": dict(Counter(s["kind"] for s in scams)),
                         "recent": [{"kind": s["kind"], "value": mask(s["kind"], s["value"]), "description": (s.get("description") or "")[:140], "created_at": s["created_at"][:10]} for s in scams[:6]]},
    }


async def list_reports(limit: int = 20, user_id: str | None = None):
    cfg = _cfg()
    if not cfg:
        return None
    url, h = cfg
    params = {"select": "id,created_at,risk_level,rule_ids,company", "order": "created_at.desc", "limit": limit}
    if user_id:
        params["user_id"] = f"eq.{user_id}"
    async with httpx.AsyncClient(timeout=4.0) as c:
        r = await c.get(f"{url}/rest/v1/reports", headers=h, params=params)
        r.raise_for_status()
        return r.json()
