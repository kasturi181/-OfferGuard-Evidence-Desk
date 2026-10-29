import os
from datetime import datetime, timezone
import httpx

API = "https://safebrowsing.googleapis.com/v4/threatMatches:find"


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


async def check_urls(urls: list[str], simulate_failure: bool = False) -> dict:
    base = {"name": "url_reputation", "source": "Google Safe Browsing", "checked_at": _now()}
    if not urls:
        return {**base, "status": "not_checked", "details": "No URLs in message."}
    if simulate_failure:
        return {**base, "status": "unavailable", "details": "Simulated provider failure. Check NOT performed."}
    key = os.getenv("SAFE_BROWSING_API_KEY")
    if not key:
        return {**base, "status": "not_checked", "details": "No API key configured. Check NOT performed."}
    body = {
        "client": {"clientId": "offerguard", "clientVersion": "0.1"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"], "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": u if u.startswith("http") else "http://" + u} for u in urls[:20]],
        },
    }
    try:
        async with httpx.AsyncClient(timeout=4.0) as c:
            r = await c.post(API, params={"key": key}, json=body)
            r.raise_for_status()
            matches = r.json().get("matches", [])
    except Exception as e:  # noqa: BLE001
        return {**base, "status": "unavailable", "details": f"Lookup failed ({type(e).__name__}). Check NOT performed."}
    if matches:
        d = "; ".join(f"{m['threat']['url']} → {m['threatType']}" for m in matches)
        return {**base, "status": "warning", "details": d}
    return {**base, "status": "no_match", "details": "No known threat match. This does NOT prove the URL is safe."}
