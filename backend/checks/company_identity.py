import re
from datetime import datetime, timezone

from extract import domain_of

SUFFIX = re.compile(r"\b(pvt|private|ltd|limited|llp|inc)\b")
SKIP_DOMAINS = {"wa.me", "t.me", "forms.gle", "bit.ly", "docs.google.com"}  # covered by RULE-09
# Common third-party sites a real recruiter may link to. Not evidence for or against the company.
NEUTRAL_DOMAINS = {"linkedin.com", "naukri.com", "indeed.com", "glassdoor.com", "glassdoor.co.in", "zoom.us", "calendly.com",
                   "meet.google.com", "teams.microsoft.com", "gov.in"}


def _skipped(d: str) -> bool:
    return d in SKIP_DOMAINS or any(d == n or d.endswith("." + n) for n in NEUTRAL_DOMAINS)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", SUFFIX.sub("", re.sub(r"[^a-z0-9 ]", " ", s.lower()))).strip()


def _is_official(dom: str, official: list[str]) -> bool:
    return any(dom == d or dom.endswith("." + d) for d in official)


def check_company(text: str, fields: dict, companies: list[dict], source: str) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def mk(name, status, details):
        return {"name": name, "status": status, "source": source, "checked_at": now, "details": details}

    t = norm(text)
    rec = next((r for r in companies if norm(r["name"]) in t), None)
    if not rec:
        who = fields.get("company") or "company"
        out = [mk("company_identity", "not_checked", f"'{who}' not found in the dataset. Live registry check NOT performed.")]
        if fields.get("registration_ids"):
            out.append(mk("registration_id_consistency", "not_checked", f"Offer states {', '.join(fields['registration_ids'])} but there is no record to compare against."))
        return out
    official = [d.lower() for d in rec.get("official_domains") or []]
    out = [mk("company_identity", "verified_match", f"'{rec['name']}' exists in the dataset. This does NOT prove the recruiter is authorized.")]

    emails = fields.get("recruiter_emails") or []
    if not emails:
        out.append(mk("email_domain_consistency", "not_checked", "No recruiter email in the message to compare."))
    else:
        dom = emails[0].split("@")[-1].lower()
        if _is_official(dom, official):
            out.append(mk("email_domain_consistency", "verified_match", f"'{dom}' matches an official domain of {rec['name']}."))
        else:
            out.append(mk("email_domain_consistency", "warning", f"Recruiter domain '{dom}' differs from known official domain(s) {official} for {rec['name']}."))

    link_domains = [d for d in fields.get("url_domains") or [] if not _skipped(d)]
    if not link_domains:
        out.append(mk("link_domain_consistency", "not_checked", "No company/careers links in the message to compare."))
    else:
        bad = [d for d in link_domains if not _is_official(d, official)]
        if bad:
            out.append(mk("link_domain_consistency", "warning", f"Link domain(s) {bad} differ from official domain(s) {official}. Official careers page: {rec.get('careers_url') or 'n/a'}."))
        else:
            out.append(mk("link_domain_consistency", "verified_match", "All links point to the official domain."))

    ids, rec_cin = fields.get("registration_ids") or [], (rec.get("cin") or "").upper()
    if ids and rec_cin:
        if rec_cin in ids:
            out.append(mk("registration_id_consistency", "verified_match", f"Registration ID {rec_cin} matches the record."))
        else:
            out.append(mk("registration_id_consistency", "warning", f"Offer states {', '.join(ids)} but the record for {rec['name']} lists {rec_cin}."))
    elif rec_cin:
        out.append(mk("registration_id_consistency", "not_checked", f"Offer states no registration ID. Ask for it and compare with {rec_cin} on the MCA portal."))
    elif ids:
        out.append(mk("registration_id_consistency", "not_checked", "Record has no registration ID to compare."))

    cities, rec_city = fields.get("cities") or [], (rec.get("city") or "").lower()
    if cities and rec_city:
        if rec_city in cities:
            out.append(mk("location_consistency", "verified_match", f"Offer mentions {rec_city.title()}, which matches the record."))
        else:
            out.append(mk("location_consistency", "warning", f"Offer mentions {', '.join(c.title() for c in cities)}; record lists {rec_city.title()}."))
    return out
