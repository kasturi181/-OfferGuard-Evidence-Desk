"""Live, key-free checks: domain age (RDAP), DNS / mail records (DNS-over-HTTPS), redirect tracing,
look-alike patterns and CIN decoding. Every lookup can fail; failures become 'unavailable', never 'safe'."""
import asyncio
import ipaddress
import os
import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import httpx

from extract import domain_of

PERSONAL = {"gmail.com", "yahoo.com", "yahoo.in", "outlook.com", "hotmail.com", "rediffmail.com", "proton.me", "protonmail.com"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "rb.gy", "cutt.ly", "is.gd", "shorturl.at", "ow.ly", "tiny.cc", "wa.me", "t.me"}
FREE_HOSTS = ("blogspot.com", "wixsite.com", "weebly.com", "github.io", "netlify.app", "vercel.app", "web.app", "firebaseapp.com",
              "000webhostapp.com", "carrd.co", "notion.site", "sites.google.com", "webflow.io", "wordpress.com", "godaddysites.com", "herokuapp.com")
RISKY_TLDS = {"xyz", "top", "click", "icu", "buzz", "work", "site", "online", "live", "shop", "vip", "rest", "cfd", "sbs", "life", "monster"}
HIRING_WORDS = re.compile(r"career|careers|job|jobs|hiring|recruit|offer|apply|join|hr|talent|vacanc|placement|opening", re.I)
SKIP_DOMAINS = {"forms.gle", "docs.google.com", "google.com", "linkedin.com", "naukri.com", "indeed.com", "mca.gov.in"}
TWO_LEVEL = {"co", "com", "org", "net", "ac", "gov", "edu", "nic"}

DOH = "https://cloudflare-dns.com/dns-query"
RDAP = "https://rdap.org/domain/"
UA = {"User-Agent": "OfferGuard/1.0 (+job-offer evidence checker)"}


def live_enabled() -> bool:
    return os.getenv("OFFERGUARD_LIVE", "1") != "0"


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def registrable(host: str) -> str:
    parts = [p for p in host.lower().strip(".").split(".") if p]
    if len(parts) <= 2:
        return ".".join(parts)
    if len(parts[-1]) == 2 and parts[-2] in TWO_LEVEL:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _mk(name, status, source, details, **extra):
    return {"name": name, "status": status, "source": source, "checked_at": _now(), "details": details, **extra}


# ---------- network helpers (each returns None on failure) ----------
async def doh(c: httpx.AsyncClient, name: str, rtype: str):
    try:
        r = await c.get(DOH, params={"name": name, "type": rtype}, headers={"accept": "application/dns-json", **UA})
        r.raise_for_status()
        j = r.json()
        return {"status": j.get("Status"), "answers": [a.get("data", "") for a in j.get("Answer", [])]}
    except Exception:  # noqa: BLE001
        return None


async def rdap_created(c: httpx.AsyncClient, domain: str):
    """Returns (datetime|None, error|None). A missing date is 'unknown', not 'old'."""
    try:
        r = await c.get(RDAP + domain, headers=UA, follow_redirects=True)
        if r.status_code == 404:
            return None, "not_found"
        r.raise_for_status()
        for e in r.json().get("events", []):
            if e.get("eventAction") == "registration" and e.get("eventDate"):
                return datetime.fromisoformat(e["eventDate"].replace("Z", "+00:00")), None
        return None, "no_date"
    except Exception:  # noqa: BLE001
        return None, "error"


def _public_ip(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_global
    except ValueError:
        return False


async def trace_redirects(c: httpx.AsyncClient, url: str, max_hops: int = 4):
    """Manual redirect walk. Refuses non-http(s), odd ports, IP literals and hosts resolving to non-public IPs."""
    hops, cur = [], url if url.lower().startswith("http") else "http://" + url
    for _ in range(max_hops + 1):
        p = urlparse(cur)
        host = (p.hostname or "").lower()
        if p.scheme not in ("http", "https") or not host or p.port not in (None, 80, 443):
            return hops, "blocked"
        try:
            ipaddress.ip_address(host)
            return hops, "blocked"
        except ValueError:
            pass
        a = await doh(c, host, "A")
        if not a or not a["answers"] or not all(_public_ip(x) for x in a["answers"] if re.match(r"^[\d.]+$", x)):
            return hops, "unresolved" if a is not None else "error"
        try:
            async with c.stream("GET", cur, headers=UA, follow_redirects=False, timeout=5.0) as r:
                hops.append((host, r.status_code))
                if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("location"):
                    cur = urljoin(cur, r.headers["location"])
                    continue
                return hops, "ok"
        except Exception:  # noqa: BLE001
            return hops, "error"
    return hops, "too_many"


# ---------- CIN decoder (offline) ----------
CIN_RE = re.compile(r"^([LU])(\d{5})([A-Z]{2})(\d{4})([A-Z]{3})(\d{6})$")
STATES = {"MH": "Maharashtra", "KA": "Karnataka", "DL": "Delhi", "TN": "Tamil Nadu", "TG": "Telangana", "AP": "Andhra Pradesh", "GJ": "Gujarat",
          "WB": "West Bengal", "UP": "Uttar Pradesh", "HR": "Haryana", "RJ": "Rajasthan", "KL": "Kerala", "MP": "Madhya Pradesh", "PB": "Punjab",
          "CH": "Chandigarh", "OR": "Odisha", "BR": "Bihar", "JH": "Jharkhand", "CT": "Chhattisgarh", "UR": "Uttarakhand", "GA": "Goa", "AS": "Assam", "HP": "Himachal Pradesh", "JK": "Jammu & Kashmir"}
CLASSES = {"PTC": "Private company", "PLC": "Public company", "OPC": "One-person company", "NPL": "Not-for-profit (Sec 8)", "GOI": "Government company",
           "FTC": "Subsidiary of foreign company", "FLC": "Foreign company (listed)", "GAP": "Govt. company (PSU)", "SGC": "State govt. company", "ULL": "Unlimited (with share capital)"}
CITY_STATE = {"bengaluru": "KA", "mumbai": "MH", "pune": "MH", "delhi": "DL", "gurugram": "HR", "noida": "UP", "hyderabad": "TG", "chennai": "TN",
              "kolkata": "WB", "ahmedabad": "GJ", "jaipur": "RJ", "kochi": "KL", "indore": "MP"}
FOUNDED = re.compile(r"(?:since|established(?: in)?|founded(?: in)?|incorporated(?: in)?|operating since)\s+(19\d{2}|20[0-3]\d)", re.I)


def decode_cin(cin: str):
    m = CIN_RE.match(cin.upper())
    if not m:
        return None
    lst, nic, st, yr, cls, serial = m.groups()
    return {"cin": cin.upper(), "listed": lst == "L", "nic": nic, "state_code": st, "state": STATES.get(st), "year": int(yr), "class_code": cls,
            "class": CLASSES.get(cls), "serial": serial}


def check_cin(text: str, fields: dict) -> list[dict]:
    ids = fields.get("registration_ids") or []
    if not ids:
        return [_mk("cin_decode", "not_checked", "Offline CIN decoder (MCA format)", "No CIN in the message. Real companies can give it on request; look it up on the MCA portal.")]
    out = []
    comp = (fields.get("company") or "").lower()
    founded = [int(x) for x in FOUNDED.findall(text)]
    for cin in ids[:2]:
        d = decode_cin(cin)
        if not d:
            out.append(_mk("cin_decode", "warning", "Offline CIN decoder (MCA format)",
                           f"{cin} is not a valid CIN format (21 characters: L/U + 5 digits + state + year + type + 6 digits).", problem="format"))
            continue
        probs, notes = [], [f"{'Listed' if d['listed'] else 'Unlisted'}", d["class"] or d["class_code"], f"state {d['state'] or d['state_code']}", f"incorporated {d['year']}"]
        if d["year"] > datetime.now(timezone.utc).year:
            probs.append(f"incorporation year {d['year']} is in the future")
        if d["state"] is None:
            probs.append(f"state code '{d['state_code']}' is not a known one")
        if d["class_code"] == "PTC" and comp and re.search(r"\blimited\b|\bltd\b", comp) and not re.search(r"private|pvt", comp):
            probs.append("name says public 'Limited' but the CIN type is a Private company (PTC)")
        if d["class_code"] == "PLC" and comp and re.search(r"private|pvt", comp):
            probs.append("name says 'Private' but the CIN type is a Public company (PLC)")
        if d["listed"] and d["class_code"] == "PTC":
            probs.append("a private company cannot be stock-exchange listed (L + PTC)")
        if founded and d["year"] > min(founded):
            probs.append(f"offer says the company existed since {min(founded)} but the CIN shows it was incorporated in {d['year']}")
        if probs:
            out.append(_mk("cin_decode", "warning", "Offline CIN decoder (MCA format)", f"{d['cin']}: " + "; ".join(probs) + ".", problem="inconsistent"))
        else:
            out.append(_mk("cin_decode", "no_match", "Offline CIN decoder (MCA format)",
                           f"{d['cin']} decodes to: " + ", ".join(notes) + ". Structure is valid. This does NOT prove the company exists. Confirm on the MCA portal."))
    return out


# ---------- offline domain-pattern check ----------
def check_patterns(fields: dict, text: str) -> dict:
    src = "Offline domain pattern analysis"
    doms = {d for d in (fields.get("url_domains") or []) if d not in SKIP_DOMAINS}
    emails = [e.split("@")[-1].lower() for e in fields.get("recruiter_emails") or []]
    doms |= {d for d in emails if d not in PERSONAL}
    if not doms:
        return _mk("domain_patterns", "not_checked", src, "No company links or recruiter-domain email in the message.")
    comp = re.sub(r"[^a-z0-9 ]", " ", (fields.get("company") or "").lower())
    tokens = [t for t in comp.split() if len(t) >= 4 and t not in ("private", "limited", "technologies", "solutions", "services", "global", "india", "systems")]
    issues = []
    for d in sorted(doms):
        reg, label, tld = registrable(d), registrable(d).split(".")[0], d.rsplit(".", 1)[-1]
        if reg in SHORTENERS:
            issues.append(f"{d} is a link shortener, so the real destination is hidden")
        if any(d == h or d.endswith("." + h) for h in FREE_HOSTS):
            issues.append(f"{d} is a free hosting / site-builder address, not a company domain")
        if tld in RISKY_TLDS:
            issues.append(f".{tld} domains are cheap and often used in scams ({d})")
        if tokens and any(t in label for t in tokens) and HIRING_WORDS.search(label.replace(next((t for t in tokens if t in label), ""), "")):
            issues.append(f"{d} imitates the company name plus a hiring word (typical look-alike pattern)")
        if label.count("-") >= 2:
            issues.append(f"{d} has several hyphens, a common look-alike trick")
    if issues:
        return _mk("domain_patterns", "warning", src, "; ".join(dict.fromkeys(issues)) + ".")
    return _mk("domain_patterns", "no_match", src, f"No suspicious pattern in: {', '.join(sorted(doms))}. This does NOT prove they are safe.")


# ---------- live network checks ----------
def _age_text(dt: datetime) -> tuple[int, str]:
    days = (datetime.now(timezone.utc) - dt).days
    when = f"{days} day{'s' if days != 1 else ''} ago" if days < 90 else (f"{days // 30} months ago" if days < 730 else f"{days // 365} years ago")
    return days, f"registered {when} ({dt.date().isoformat()})"


async def check_live(fields: dict, text: str) -> list[dict]:
    """Domain age, DNS/MX and redirect checks. Always returns check dicts; never raises."""
    names = ["domain_age", "dns_mail_records", "link_redirects"]
    if not live_enabled():
        return [_mk(n, "not_checked", "Live lookups disabled on this server", "Live lookups are switched off (OFFERGUARD_LIVE=0). Check NOT performed.") for n in names]
    link_doms = [d for d in dict.fromkeys(fields.get("url_domains") or []) if d not in SKIP_DOMAINS and d not in SHORTENERS]
    mail_doms = [d for d in dict.fromkeys(e.split("@")[-1].lower() for e in fields.get("recruiter_emails") or []) if d not in PERSONAL]
    targets = list(dict.fromkeys([registrable(d) for d in link_doms + mail_doms]))[:4]
    urls = [u for u in (fields.get("urls") or [])][:2]
    if not targets and not urls:
        return [_mk(n, "not_checked", "Live lookups", "No company link or company-domain email in the message to look up.") for n in names]

    async def run():
        async with httpx.AsyncClient(timeout=5.0) as c:
            age_t = [rdap_created(c, d) for d in targets]
            dns_t = [doh(c, d, "A") for d in targets]
            mx_t = [doh(c, d, "MX") for d in mail_doms[:2]]
            red_t = [trace_redirects(c, u) for u in urls]
            return await asyncio.gather(asyncio.gather(*age_t), asyncio.gather(*dns_t), asyncio.gather(*mx_t), asyncio.gather(*red_t))

    try:
        ages, a_recs, mx_recs, reds = await asyncio.wait_for(run(), timeout=14)
    except Exception:  # noqa: BLE001
        return [_mk(n, "unavailable", "Live lookups (RDAP, DNS-over-HTTPS)", "Lookup timed out or failed. Check NOT performed.") for n in names]

    out = []
    # domain age
    lines, young, ok, bad = [], [], 0, 0
    for d, (dt, err) in zip(targets, ages):
        if dt:
            days, txt = _age_text(dt)
            lines.append(f"{d}: {txt}")
            ok += 1
            if days < 180:
                young.append(days)
        elif err == "not_found":
            lines.append(f"{d}: no registration record found (RDAP)")
            bad += 1
        else:
            lines.append(f"{d}: age unknown (lookup failed or hidden)")
    src = "RDAP public registry (rdap.org)"
    if young:
        out.append(_mk("domain_age", "warning", src, "; ".join(lines) + ". New domains are a common scam sign.", min_age_days=min(young)))
    elif ok:
        out.append(_mk("domain_age", "no_match", src, "; ".join(lines) + ". Age alone does not prove a domain is safe."))
    else:
        out.append(_mk("domain_age", "unavailable", src, "; ".join(lines) + ". Check NOT completed."))

    # DNS + mail
    dl, dbad, got = [], [], 0
    for d, a in zip(targets, a_recs):
        if a is None:
            dl.append(f"{d}: lookup failed")
        elif a["status"] == 3 or (a["status"] == 0 and not a["answers"]):
            dl.append(f"{d}: does NOT resolve (no website)")
            dbad.append(d)
            got += 1
        else:
            dl.append(f"{d}: resolves")
            got += 1
    for d, m in zip(mail_doms[:2], mx_recs):
        if m is None:
            dl.append(f"mail for {d}: lookup failed")
        elif not m["answers"]:
            dl.append(f"{d}: has NO mail server, so it cannot receive replies")
            dbad.append(d)
            got += 1
        else:
            dl.append(f"mail for {d}: mail server found")
            got += 1
    src = "DNS-over-HTTPS (Cloudflare)"
    out.append(_mk("dns_mail_records", "warning" if dbad else ("no_match" if got else "unavailable"), src,
                   "; ".join(dl) + (". A company that recruits should have a working website and mail server." if dbad else ". Existing records do not prove legitimacy.")))

    # redirects
    if not urls:
        out.append(_mk("link_redirects", "not_checked", "Redirect tracing", "No link in the message to open."))
    else:
        rl, flag, done = [], False, 0
        for u, (hops, state) in zip(urls, reds):
            if state == "blocked":
                rl.append(f"{domain_of(u)}: skipped for safety (unusual address)")
                continue
            if not hops:
                rl.append(f"{domain_of(u)}: could not be reached ({state})")
                continue
            done += 1
            first, last = registrable(hops[0][0]), registrable(hops[-1][0])
            chain = " → ".join(h for h, _ in hops)
            if first != last:
                flag = True
                rl.append(f"{chain}: lands on a DIFFERENT site ({last})")
            else:
                rl.append(f"{chain}: no cross-site redirect (HTTP {hops[-1][1]})")
        out.append(_mk("link_redirects", "warning" if flag else ("no_match" if done else "unavailable"), "Server-side redirect tracing (page content not downloaded)",
                       "; ".join(rl) + ("." if rl else "")))
    return out
