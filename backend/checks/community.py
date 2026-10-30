from collections import Counter
from datetime import datetime, timezone

import db
from checks.company_identity import norm
from rules import PERSONAL

AUTO_MIN_REPORTERS = 2  # an auto-learned signal needs this many different reporters before it is shown


async def check_community(fields: dict) -> dict:
    base = {"name": "community_reports", "source": "OfferGuard user reports + earlier high-risk checks (unverified)",
            "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "count": 0}
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

    users: Counter = Counter()
    autos: dict[tuple[str, str], set] = {}
    for r in rows:
        key = (r.get("kind"), r.get("value"))
        if key not in wanted:
            continue
        if r.get("source") == "auto":
            autos.setdefault(key, set()).add(r.get("reporter") or r.get("id"))
        else:
            users[key] += 1

    parts, total = [], 0
    for key in sorted(set(users) | set(autos)):
        u = users.get(key, 0)
        a = len(autos.get(key, ()))
        a = a if a >= AUTO_MIN_REPORTERS else 0
        if not (u or a):
            continue
        bits = []
        if u:
            bits.append(f"{u} user report{'s' if u > 1 else ''}")
        if a:
            bits.append(f"seen in {a} earlier high-risk checks")
        parts.append(f"{key[0]} '{db.mask(*key)}' ({', '.join(bits)})")
        total += u + a
    if not parts:
        return {**base, "status": "no_match", "details": "No matching reports. This does NOT mean the offer is safe."}
    return {**base, "status": "warning", "count": total,
            "details": "Matches: " + "; ".join(parts) + ". Reports and auto-detected signals are unverified."}
