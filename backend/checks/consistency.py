"""Cross-source consistency check (Innovation A). Pure function.

check_consistency(fields) compares company name, recruiter email domain,
URL domains, location and registration id. Each comparison is reported
on its own: status = match | mismatch | not_checked. Never "safe".

Expected keys in `fields` (all optional, missing -> not_checked):
    company_name: str
    emails: list[str]          (or recruiter_emails)
    urls: list[str]
    careers_domain: str        (from your company record, if known)
    location: str              (offer letter)
    record_location: str       (company record)
    registration_id: str       (CIN)
"""
from __future__ import annotations
import re
from urllib.parse import urlparse

FREE_MAIL = {"gmail.com", "yahoo.com", "yahoo.in", "outlook.com", "hotmail.com",
             "rediffmail.com", "proton.me", "protonmail.com", "icloud.com"}
CIN_RE = re.compile(r"^[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$")
_STOP = {"pvt", "ltd", "private", "limited", "llp", "inc", "corp", "the", "and",
         "technologies", "technology", "solutions", "services", "india", "co"}


def _row(check, status, detail, evidence=None, unverified=None):
    return {"check": check, "status": status, "detail": detail,
            "evidence": evidence or [], "unverified": unverified}


def _email_domain(e: str) -> str:
    return e.rsplit("@", 1)[-1].strip().lower() if "@" in e else ""


def _url_domain(u: str) -> str:
    if "//" not in u:
        u = "http://" + u
    host = (urlparse(u).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def _root(d: str) -> str:
    parts = d.split(".")
    if len(parts) >= 3 and parts[-2] in {"co", "com", "org", "net", "ac", "gov"}:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _tokens(name: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", name.lower()) if t not in _STOP and len(t) > 2]


def check_consistency(fields: dict | None) -> list[dict]:
    f = fields or {}
    company = (f.get("company_name") or "").strip()
    emails = f.get("emails") or f.get("recruiter_emails") or []
    urls = f.get("urls") or []
    e_domains = sorted({_email_domain(e) for e in emails if _email_domain(e)})
    u_domains = sorted({_url_domain(u) for u in urls if _url_domain(u)})
    out = []

    # 1. company name vs recruiter email domain
    if not company or not e_domains:
        out.append(_row("Company name vs recruiter email domain", "not_checked",
                        "Need both a company name and a recruiter email.",
                        unverified="Company name or email not found in the text."))
    else:
        toks = _tokens(company)
        corp = [d for d in e_domains if d not in FREE_MAIL]
        if not corp:
            out.append(_row("Company name vs recruiter email domain", "mismatch",
                            f"Recruiter uses a free mailbox ({', '.join(e_domains)}), not a company domain.",
                            [company] + e_domains))
        elif any(t in _root(d) for d in corp for t in toks):
            out.append(_row("Company name vs recruiter email domain", "match",
                            f"Domain {', '.join(corp)} contains part of the company name. A name match does not prove the recruiter is authorized.",
                            [company] + corp,
                            "Recruiter authorization is not verified."))
        else:
            out.append(_row("Company name vs recruiter email domain", "mismatch",
                            f"'{company}' does not appear in {', '.join(corp)}.",
                            [company] + corp))

    # 2. recruiter email domain vs link domains
    if not e_domains or not u_domains:
        out.append(_row("Email domain vs link domain", "not_checked",
                        "Need both an email and a link in the message."))
    else:
        er = {_root(d) for d in e_domains}
        ur = {_root(d) for d in u_domains}
        if er & ur:
            out.append(_row("Email domain vs link domain", "match",
                            "At least one link uses the same domain as the recruiter email.",
                            sorted(er | ur)))
        else:
            out.append(_row("Email domain vs link domain", "mismatch",
                            "Links point to a different domain than the recruiter email.",
                            sorted(er | ur)))

    # 3. careers-page domain from record vs links
    careers = (f.get("careers_domain") or "").lower()
    if not careers:
        out.append(_row("Link domain vs official careers page", "not_checked",
                        "No official careers domain on record for this company.",
                        unverified="Look it up yourself on the official website."))
    elif not u_domains:
        out.append(_row("Link domain vs official careers page", "not_checked",
                        "No link in the message to compare."))
    elif _root(careers) in {_root(d) for d in u_domains}:
        out.append(_row("Link domain vs official careers page", "match",
                        f"A link uses the known careers domain {careers}.", [careers] + u_domains))
    else:
        out.append(_row("Link domain vs official careers page", "mismatch",
                        f"Known careers domain is {careers}; message links go to {', '.join(u_domains)}.",
                        [careers] + u_domains))

    # 4. location
    loc, rec = (f.get("location") or "").strip().lower(), (f.get("record_location") or "").strip().lower()
    if not loc or not rec:
        out.append(_row("Offer location vs company record", "not_checked",
                        "Location missing in the message or in the record."))
    elif rec in loc or loc in rec:
        out.append(_row("Offer location vs company record", "match", "Locations overlap.", [loc, rec]))
    else:
        out.append(_row("Offer location vs company record", "mismatch",
                        "Offer location differs from the company record. Remote or branch offices can explain this.",
                        [loc, rec]))

    # 5. registration id
    rid = (f.get("registration_id") or "").strip().upper()
    if not rid:
        out.append(_row("Registration ID (CIN) format", "not_checked",
                        "No registration id in the message.",
                        unverified="Ask for the CIN and check it on mca.gov.in."))
    elif CIN_RE.match(rid):
        out.append(_row("Registration ID (CIN) format", "match",
                        "Format is valid. The number itself is not looked up in the registry.",
                        [rid], "Existence of this CIN on MCA is not verified."))
    else:
        out.append(_row("Registration ID (CIN) format", "mismatch",
                        "Does not look like a valid 21-character CIN.", [rid]))
    return out
