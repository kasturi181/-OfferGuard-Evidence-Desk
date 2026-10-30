"""Website details for every company-looking domain in the offer: registration date and age (RDAP, free, no key).

A very new website is a WEAK signal on its own (RULE-15). Failures are reported as "unavailable", never as safe.
Many country registries do not publish RDAP, so "no record" is common and means little.
"""
import asyncio
import os
from datetime import datetime, timezone

import httpx

NEW_DAYS = 90
MAX_DOMAINS = 3
TIMEOUT = 6.0
PERSONAL = {"gmail.com", "yahoo.com", "yahoo.in", "outlook.com", "hotmail.com", "rediffmail.com", "proton.me", "protonmail.com"}
SKIP = PERSONAL | {"wa.me", "t.me", "bit.ly", "forms.gle", "docs.google.com", "google.com", "linkedin.com", "naukri.com",
                   "indeed.com", "glassdoor.com", "zoom.us", "calendly.com", "microsoft.com", "facebook.com", "instagram.com"}
SOURCE = "RDAP public registration data (rdap.org)"


def pick_domains(fields: dict) -> list[str]:
    cands = list(fields.get("url_domains") or []) + [e.split("@")[-1].lower() for e in fields.get("recruiter_emails") or []]
    out = []
    for d in cands:
        d = d.lower().strip(".")
        if d and "." in d and d not in SKIP and not any(d.endswith("." + s) for s in SKIP) and d not in out:
            out.append(d)
    return out[:MAX_DOMAINS]


def parse_rdap(data: dict, domain: str, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    reg = next((e.get("eventDate") for e in data.get("events", []) if e.get("eventAction") == "registration"), None)
    registrar = None
    for ent in data.get("entities", []):
        if "registrar" in (ent.get("roles") or []):
            for item in (ent.get("vcardArray") or [None, []])[1]:
                if item and item[0] == "fn":
                    registrar = item[3]
    if not reg:
        return {"domain": domain, "status": "unavailable", "note": "The registry did not publish a registration date."}
    when = datetime.fromisoformat(reg.replace("Z", "+00:00"))
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    age = (now - when).days
    return {"domain": domain, "status": "ok", "registered": when.date().isoformat(), "age_days": age, "registrar": registrar,
            "is_new": age < NEW_DAYS}


async def _one(client: httpx.AsyncClient, domain: str) -> dict:
    try:
        r = await client.get(f"https://rdap.org/domain/{domain}", follow_redirects=True)
        if r.status_code == 404:
            return {"domain": domain, "status": "unavailable", "note": "No public registration record. Some country registries do not publish one."}
        r.raise_for_status()
        return parse_rdap(r.json(), domain)
    except Exception:  # noqa: BLE001
        return {"domain": domain, "status": "unavailable", "note": "Lookup failed or timed out."}


async def domain_intel(domains: list[str], simulate_failure: bool = False) -> list[dict]:
    if not domains:
        return []
    if simulate_failure or os.getenv("OFFERGUARD_OFFLINE"):  # offline switch is used by the tests so they never touch the network
        return [{"domain": d, "status": "unavailable", "note": "Simulated failure." if simulate_failure else "Offline mode."} for d in domains]
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        return list(await asyncio.gather(*[_one(c, d) for d in domains]))


def age_check(intel: list[dict]) -> dict:
    base = {"name": "domain_age", "source": SOURCE, "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "count": 0}
    if not intel:
        return {**base, "status": "not_checked", "details": "No company website or company email domain in the message to look up."}
    found = [i for i in intel if i["status"] == "ok"]
    if not found:
        return {**base, "status": "unavailable", "details": "Registration date could not be looked up. Check NOT performed."}
    new = [i for i in found if i["is_new"]]
    if new:
        return {**base, "status": "warning", "details": "; ".join(f"{i['domain']} was registered {i['age_days']} days ago ({i['registered']})" for i in new) + "."}
    return {**base, "status": "no_match", "details": "; ".join(f"{i['domain']} registered {i['registered']} ({i['age_days']} days ago)" for i in found) + ". An old domain is not proof of a real employer."}
