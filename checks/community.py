from collections import Counter
from datetime import datetime, timezone

import db
from checks.company_identity import norm
from rules import PERSONAL


async def check_community(fields: dict) -> dict:
    base = {"name": "community_reports", "source": "OfferGuard user reports (unverified)",
            "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    wanted: set[tuple[str, str]] = set()
    for e in fields.get("recruiter_emails", []):
        wanted.add(("email", db.clean(e)))
        dom = e.split("@")[-1].lower()
        if dom not in PERSONAL:
            wanted.add(("domain", db.clean(dom)))
    for d in fields.get("url_domains", []):
        wanted.add(("domain", db.clean(d)))
    for p in fields.get("phones", []):
        wanted.add(("phone", p))
    if fields.get("company"):
        wanted.add(("company", db.clean(norm(fields["company"]))))
    status, rows = await db.find_scam_reports([v for _, v in wanted])
    if status == "disabled":
        return {**base, "status": "not_checked", "details": "Database not configured. Community report lookup NOT performed."}
    if status == "error":
        return {**base, "status": "unavailable", "details": "Community report lookup failed. Check NOT performed."}
    hits = Counter((r["kind"], r["value"]) for r in rows if (r["kind"], r["value"]) in wanted)
    if not hits:
        return {**base, "status": "no_match", "details": "No matching user reports. This does NOT mean the offer is safe."}
    parts = [f"{k} '{db.mask(k, v)}' ({n} report{'s' if n > 1 else ''})" for (k, v), n in hits.items()]
    return {**base, "status": "warning", "details": "Matching user reports: " + "; ".join(parts) + ". Reports are unverified."}
