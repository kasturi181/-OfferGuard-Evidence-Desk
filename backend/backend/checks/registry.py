"""Company registry lookup via OpenCorporates (needs OPENCORPORATES_API_TOKEN).

No token -> status "unavailable" (shown under Not checked, never "safe").
A name match does NOT prove the recruiter is authorized.
Swap this one function if you later use another registry.
"""
from __future__ import annotations
import os
import re

TIMEOUT = 8.0
_STOP = {"pvt", "ltd", "private", "limited", "llp", "inc", "corp", "the", "and", "co"}


def _norm(s: str) -> str:
    return " ".join(t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in _STOP)


def _check(status, detail, **extra):
    return {"id": "registry", "name": "Company registry (OpenCorporates, India)", "status": status,
            "detail": detail, "source": "OpenCorporates", **extra}


async def check_registry(company: str | None, simulate_failure: bool = False) -> dict:
    name = (company or "").strip()
    if len(name) < 3:
        return _check("not_checked", "No company name extracted.")
    token = os.getenv("OPENCORPORATES_API_TOKEN")
    if not token:
        return _check("unavailable", "Registry lookup not configured on this server.")
    if simulate_failure:
        return _check("unavailable", "Simulated failure.")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.get("https://api.opencorporates.com/v0.4/companies/search",
                            params={"q": name, "jurisdiction_code": "in", "per_page": 5, "api_token": token})
        r.raise_for_status()
        items = [x["company"] for x in r.json().get("results", {}).get("companies", [])]
        target = _norm(name)
        for co in items:
            if _norm(co.get("name", "")) == target:
                return _check("verified_match",
                              f"Found '{co['name']}' ({co.get('current_status') or 'status unknown'}). "
                              "A record match does not prove this recruiter or vacancy is real.",
                              registration_id=co.get("company_number"), url=co.get("opencorporates_url"))
        return _check("no_match", "No exact name match in the registry results. The name may be spelled differently.")
    except Exception:
        return _check("unavailable", "Registry lookup failed or timed out.")
