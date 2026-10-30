"""Auto-learned community signal.

Scam campaigns reuse the same phone numbers, emails and domains across many victims. When an analysis
finds a STRONG text-based warning (upfront payment or OTP request), we remember the recruiter's contact
details. The next person who gets the same details sees "seen in earlier high-risk checks".

Safeguards (so nobody can poison the list or smear a real company):
  - only after RULE-01 or RULE-02 matched
  - never well-known sites, link shorteners, or domains of companies in our verified list
  - an auto signal is shown only after >= 2 DIFFERENT reporters (see checks/community.py)
  - it is always shown as a weak/medium, unverified signal, never as a verdict
"""
from checks.company_identity import _is_official
from rules import PERSONAL
import db

TRIGGER_RULES = {"RULE-01", "RULE-02"}
NEVER_LEARN = (
    "google.com", "linkedin.com", "naukri.com", "indeed.com", "glassdoor.com", "glassdoor.co.in", "facebook.com",
    "instagram.com", "youtube.com", "microsoft.com", "zoom.us", "calendly.com", "github.com", "wa.me", "t.me",
    "bit.ly", "forms.gle", "gov.in", "nic.in", "whatsapp.com", "telegram.org", "docs.google.com",
)
MAX_SIGNALS = 8


def _blocked(domain: str, companies: list[dict]) -> bool:
    if any(domain == d or domain.endswith("." + d) for d in NEVER_LEARN):
        return True
    for rec in companies or []:
        if _is_official(domain, [x.lower() for x in rec.get("official_domains") or []]):
            return True
    return False


def signals_from(fields: dict, findings: list[dict], companies: list[dict] | None = None) -> list[tuple[str, str]]:
    if not TRIGGER_RULES & {f.get("rule_id") for f in findings}:
        return []
    out: list[tuple[str, str]] = []
    for e in fields.get("recruiter_emails", []):
        dom = e.split("@")[-1].lower()
        if _blocked(dom, companies or []):
            continue
        out.append(("email", db.clean(e)))
        if dom not in PERSONAL:
            out.append(("domain", db.clean(dom)))
    for d in fields.get("url_domains", []):
        if not _blocked(d, companies or []):
            out.append(("domain", db.clean(d)))
    for p in fields.get("phones", []):
        out.append(("phone", p))
    seen, uniq = set(), []
    for item in out:
        if item not in seen:
            seen.add(item)
            uniq.append(item)
    return uniq[:MAX_SIGNALS]
