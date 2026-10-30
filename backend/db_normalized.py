"""Persist one analysis into normalized Supabase tables. Never raises.

Privacy: input text is redacted (emails, phone numbers, long digit runs) before storage,
and only stored at all if STORE_INPUT_TEXT=true. Default stores a hash + length only.
"""
from __future__ import annotations
import hashlib
import logging
import os
import re

import db_extra

log = logging.getLogger("offerguard.db")
_REDACT = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+|\+?\d[\d\s-]{7,}\d|\b\d{9,}\b")


def redact(text: str) -> str:
    return _REDACT.sub("[removed]", text or "")


async def _post(table: str, rows, returning: bool = False):
    import httpx
    headers = db_extra._headers({"Prefer": "return=representation" if returning else "return=minimal"})
    async with httpx.AsyncClient(timeout=db_extra.TIMEOUT) as c:
        r = await c.post(db_extra._url(table), headers=headers, json=rows)
        r.raise_for_status()
        return r.json() if returning else None


async def save_submission(text: str, report: dict, source: str = "paste", simulate_failure: bool = False):
    """Returns submission id (str) or None. Call after enrich_report; failure must not break /analyze."""
    if not db_extra.configured():
        return None
    try:
        keep = os.getenv("STORE_INPUT_TEXT", "false").lower() == "true"
        sub = await _post("submissions", {
            "source": source if source in ("paste", "pdf") else "paste",
            "input_redacted": redact(text)[:20000] if keep else None,
            "input_sha256": hashlib.sha256((text or "").encode()).hexdigest(),
            "char_count": len(text or ""), "simulate_failure": bool(simulate_failure)}, returning=True)
        sid = sub[0]["id"]

        fields = report.get("extracted_fields") or {}
        frows = []
        for k, v in fields.items():
            for item in (v if isinstance(v, list) else [v]):
                if item not in (None, "") and not isinstance(item, (dict, list)):
                    frows.append({"submission_id": sid, "field_key": k, "field_value": str(item)[:300]})
        if frows:
            await _post("extracted_fields", frows)

        findings = []
        for f in report.get("findings") or []:
            if not isinstance(f, dict):
                continue
            sev = str(f.get("severity", "info")).lower()
            findings.append({
                "submission_id": sid, "rule_id": str(f.get("id") or f.get("rule") or "")[:60],
                "title": str(f.get("title") or f.get("claim") or "")[:200],
                "severity": sev if sev in ("strong", "medium", "weak", "info") else "info",
                "matched_text": str(f.get("matched_text") or "")[:300],
                "source": str(f.get("source") or "")[:120], "status": str(f.get("status") or "")[:30],
                "confidence": str(f.get("confidence") or "")[:20],
                "unverified": str(f.get("unverified") or f.get("uncertainty") or "")[:300]})
        if findings:
            await _post("findings", findings)

        v = report.get("verdict_detail") or {}
        await _post("reports", {
            "submission_id": sid, "risk_level": (report.get("assessment") or {}).get("level"),
            "verdict": report.get("verdict"), "score": v.get("score"),
            "mode": report.get("mode"), "report": report})
        return sid
    except Exception:
        log.exception("save_submission failed")
        return None
