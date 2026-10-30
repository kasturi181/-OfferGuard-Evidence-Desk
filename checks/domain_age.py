"""Domain age via RDAP (free, no key). Weak signal only.

check_domain_age(domain) -> check dict. Never raises.
status: warning (< NEW_DAYS old) | no_match (older) | unavailable | not_checked
"""
from __future__ import annotations
import re
from datetime import datetime, timezone

NEW_DAYS = 90
TIMEOUT = 6.0
_DOMAIN = re.compile(r"^(?=.{4,253}$)([a-z0-9-]{1,63}\.)+[a-z]{2,24}$")
FREE_MAIL = {"gmail.com", "yahoo.com", "yahoo.in", "outlook.com", "hotmail.com",
             "rediffmail.com", "proton.me", "protonmail.com", "icloud.com"}


def _check(status, detail, domain=None, age=None):
    return {"id": "domain_age", "name": "Domain registration age", "status": status,
            "detail": detail, "source": "RDAP (rdap.org)", "domain": domain, "age_days": age}


async def check_domain_age(domain: str | None, simulate_failure: bool = False) -> dict:
    d = (domain or "").strip().lower()
    if not d or d in FREE_MAIL or not _DOMAIN.match(d):
        return _check("not_checked", "No company domain to look up.", d or None)
    if simulate_failure:
        return _check("unavailable", "Simulated failure.", d)
    try:
        import httpx
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as c:
            r = await c.get(f"https://rdap.org/domain/{d}")
        if r.status_code == 404:
            return _check("unavailable", "Registry has no record for this domain.", d)
        r.raise_for_status()
        events = r.json().get("events", [])
        reg = next((e["eventDate"] for e in events if e.get("eventAction") == "registration"), None)
        if not reg:
            return _check("unavailable", "Registration date not published.", d)
        when = datetime.fromisoformat(reg.replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - when).days
        if age < NEW_DAYS:
            return _check("warning", f"{d} was registered {age} days ago.", d, age)
        return _check("no_match", f"{d} was registered {age} days ago. Age alone does not make a site trustworthy.", d, age)
    except Exception:
        return _check("unavailable", "Lookup failed or timed out.", d)
