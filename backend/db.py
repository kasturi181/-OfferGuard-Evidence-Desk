"""Optional Supabase persistence over REST. No-op if env vars missing."""
import os
import httpx


def _cfg():
    u, k = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY")
    return (u.rstrip("/"), {"apikey": k, "Authorization": f"Bearer {k}", "Content-Type": "application/json"}) if u and k else None


async def save_report(text: str, report: dict) -> bool:
    cfg = _cfg()
    if not cfg:
        return False
    url, h = cfg
    try:
        async with httpx.AsyncClient(timeout=3.0) as c:
            r = await c.post(f"{url}/rest/v1/reports", headers=h, json={"input_text": text[:20000], "report": report, "risk_level": report["assessment"]["level"]})
            return r.status_code < 300
    except Exception:  # noqa: BLE001
        return False


async def list_reports(limit: int = 20):
    cfg = _cfg()
    if not cfg:
        return None
    url, h = cfg
    async with httpx.AsyncClient(timeout=4.0) as c:
        r = await c.get(f"{url}/rest/v1/reports", headers=h, params={"select": "id,created_at,risk_level,input_text", "order": "created_at.desc", "limit": limit})
        return r.json()
