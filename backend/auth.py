"""Optional Supabase Auth helpers. Everything degrades gracefully: no token or no config -> anonymous.

The frontend signs users in with Supabase (magic link). It sends the access token as
`Authorization: Bearer <token>`. We ask Supabase who the token belongs to, so no JWT secret is needed here.
"""
import hashlib
import os
import time
from collections import defaultdict, deque

import httpx

_hits: dict[str, deque] = defaultdict(deque)


def _cfg():
    u, k = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY")
    return (u.rstrip("/"), k) if u and k else None


def login_required_for_reports() -> bool:
    return os.getenv("REQUIRE_LOGIN_FOR_REPORTS", "").strip().lower() == "true"


async def current_user(request) -> dict | None:
    """Returns {"id", "email"} for a valid Supabase session token, else None. Never raises."""
    if request is None:
        return None
    header = request.headers.get("authorization", "")
    cfg = _cfg()
    if not cfg or not header.lower().startswith("bearer "):
        return None
    token = header[7:].strip()
    if len(token) < 20:
        return None
    url, key = cfg
    try:
        async with httpx.AsyncClient(timeout=3.0) as c:
            r = await c.get(f"{url}/auth/v1/user", headers={"apikey": key, "Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            d = r.json()
            if d.get("id"):
                return {"id": d["id"], "email": d.get("email")}
    except Exception:  # noqa: BLE001
        pass
    return None


def client_id(request, user: dict | None = None) -> str:
    """Stable, non-reversible id for de-duplication and rate limits. Raw IPs are never stored."""
    if user:
        return "u:" + user["id"]
    ip = "unknown"
    if request is not None:
        fwd = request.headers.get("x-forwarded-for", "")
        ip = fwd.split(",")[0].strip() or (request.client.host if request.client else "unknown")
    salt = os.getenv("SUPABASE_SERVICE_KEY", "offerguard")
    return "ip:" + hashlib.sha256((salt + ip).encode()).hexdigest()[:20]


def rate_ok(key: str, limit: int = 5, window: int = 3600) -> bool:
    """Tiny in-memory limiter (single instance). Returns False when the caller is over the limit."""
    now, q = time.time(), _hits[key]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= limit:
        return False
    q.append(now)
    return True
