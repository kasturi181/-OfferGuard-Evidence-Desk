"""Deterministic rules. No FastAPI, no network. Same logic everywhere."""
import re
from extract import PAYMENT

PERSONAL = ("gmail.com", "yahoo.com", "yahoo.in", "outlook.com", "hotmail.com", "rediffmail.com", "proton.me", "protonmail.com")
LOW_SKILL = re.compile(r"\b(fresher|intern(?:ship)?|data entry|typing|part[- ]time|work from home|wfh|form filling)\b", re.I)

CRED = re.compile(r"(?:share|send|provide|give|tell|enter)[^.\n]{0,40}\b(?:otp|password|pin|cvv|upi pin|net ?banking|card number|bank (?:login|credentials))\b[^.\n]{0,20}", re.I)
DOCS = re.compile(r"(?:send|share|submit|upload|provide)[^.\n]{0,50}\b(?:aadhaar|aadhar|pan card|passport|bank (?:account|statement|details)|passbook|cancelled cheque)\b[^.\n]{0,20}", re.I)
URGENT = re.compile(r"(?:guaranteed (?:job|selection|placement)|100%\s*(?:selection|placement|job)|confirmed selection|within \d+\s*(?:hours?|minutes?)|last chance|today only|limited (?:seats|slots)|act (?:now|immediately)|respond immediately)[^.\n]{0,30}", re.I)
REDIRECT = re.compile(r"(?:telegram|whatsapp)[^.\n]{0,50}|(?:wa\.me|t\.me|forms\.gle|bit\.ly|docs\.google\.com/forms)/\S+", re.I)

LIMITS = [
    "Warning signals are not proof of fraud. Absence of signals is not proof of safety.",
    "A company-record match shows an entity may exist; it does not prove the recruiter is authorized.",
    "Company records come from a small synthetic sample dataset, not an official registry.",
    "Scanned/image PDFs are not supported (no OCR).",
]


def _f(rule_id, severity, title, claim, text, m, why, action, status="matched_rule", unc="Text observation only; context outside the message is unknown."):
    return {
        "rule_id": rule_id, "severity": severity, "title": title, "claim": claim,
        "evidence": m.group(0).strip() if m else text, "start": m.start() if m else None,
        "end": m.end() if m else None, "source": "User-provided message", "why": why,
        "status": status, "uncertainty": unc, "action": action,
    }


def run_rules(text: str, fields: dict, checks: list[dict]) -> list[dict]:
    out = []
    if m := PAYMENT.search(text):
        out.append(_f("RULE-01", "strong", "Upfront payment request", "The message asks the candidate to pay before securing the job.", text, m,
                      "Upfront recruitment fees are a common warning sign and warrant independent verification.", "Do not pay until the opportunity is verified through the company's official channels."))
    if m := CRED.search(text):
        out.append(_f("RULE-02", "strong", "Credential / OTP request", "The message asks for OTP, password, PIN or banking credentials.", text, m,
                      "Legitimate hiring does not need OTPs, PINs or passwords.", "Never share credentials. Stop replying and report to the platform you found it on."))
    for c in checks:
        if c["name"] == "url_reputation" and c["status"] == "warning":
            out.append({"rule_id": "RULE-03", "severity": "strong", "title": "URL on reputation threat list", "claim": "A link in the message is flagged by a reputation provider.",
                        "evidence": c["details"], "start": None, "end": None, "source": c["source"] + f" (checked {c['checked_at']})",
                        "why": "Flagged URLs may host phishing or malware. Advisory by Google Safe Browsing.", "status": "warning",
                        "uncertainty": "Provider lists can contain errors; treat as potential risk.", "action": "Do not open the link."})
        if c["name"] == "company_identity" and c["status"] == "warning":
            out.append({"rule_id": "RULE-04", "severity": "medium", "title": "Recruiter domain inconsistent with company record", "claim": "Recruiter email domain differs from the known official domain.",
                        "evidence": c["details"], "start": None, "end": None, "source": c["source"] + f" (checked {c['checked_at']})",
                        "why": "Real companies can be impersonated with look-alike domains.", "status": "warning",
                        "uncertainty": "Mismatch means unverified, not proven fraud. Company may use other domains.", "action": "Find the company's official careers page yourself and confirm the recruiter there."})
    comp = fields.get("company")
    for e in fields["recruiter_emails"]:
        dom = e.split("@")[-1].lower()
        if dom in PERSONAL and (comp or re.search(r"\b(hr|recruit|hiring|talent)\b", text, re.I)):
            m = re.search(re.escape(e), text)
            out.append(_f("RULE-05", "medium", "Personal email for corporate hiring", f"Recruiter for {comp or 'a company'} uses {dom}.", text, m,
                          "Corporate hiring normally uses company-domain email.", "Ask for a company-domain email and verify it independently.",
                          status="warning", unc="Small firms and startups sometimes use personal email."))
            break
    if m := DOCS.search(text):
        out.append(_f("RULE-06", "medium", "Sensitive documents requested early", "The message requests identity or banking documents.", text, m,
                      "Identity/bank documents are normally collected after a verified offer.", "Share nothing sensitive until the employer is verified."))
    if m := URGENT.search(text):
        out.append(_f("RULE-07", "medium", "Guaranteed selection or pressure", "The message guarantees selection or pressures quick action.", text, m,
                      "Pressure and guarantees reduce time to verify.", "Take time. Verify before acting."))
    if LOW_SKILL.search(text):
        for s in fields["salaries"]:
            if s["monthly_inr"] >= 75_000 or (s["period"] == "day" and s["monthly_inr"] >= 130_000):
                m = re.compile(re.escape(s["raw"])).search(text)
                out.append(_f("RULE-08", "medium", "Implausible salary", f"~₹{s['monthly_inr']:,}/month offered for an entry-level / low-skill role.", text, m,
                              "Pay far above market for the described role is a common lure.", "Compare against listings for the same role on trusted job boards.",
                              status="warning", unc="Rule-of-thumb threshold (₹75,000/month), not market data."))
                break
    if m := REDIRECT.search(text):
        out.append(_f("RULE-09", "weak", "Redirect to messaging app / external form", "Applicant is sent to an unverified chat or form.", text, m,
                      "Moves the conversation off verifiable channels.", "Prefer the company's official application portal.",
                      status="warning", unc="Many real recruiters also use WhatsApp."))
    ci = next((c for c in checks if c["name"] == "company_identity"), None)
    if (not ci) or ci["status"] in ("not_checked", "unavailable"):
        out.append({"rule_id": "RULE-10", "severity": "info", "title": "Company / recruiter not independently verified", "claim": "No source confirms the company or the recruiter's authority.",
                    "evidence": ci["details"] if ci else "No company check ran.", "start": None, "end": None, "source": "OfferGuard checks", "why": "Missing evidence is not evidence of safety.",
                    "status": "unavailable", "uncertainty": "Sample dataset is tiny; absence here means little.", "action": "Verify the company on the MCA portal and the recruiter via the official website."})
    return out


def assess(findings: list[dict]) -> dict:
    n = {s: sum(1 for f in findings if f["severity"] == s) for s in ("strong", "medium", "weak", "info")}
    if n["strong"]:
        level, summary = "high", "Strong warning signal(s) found. Verify independently before any action."
    elif n["medium"] >= 2:
        level, summary = "elevated", "Multiple medium signals. Verify before proceeding."
    elif n["medium"] or n["weak"]:
        level, summary = "some", "Some signals found. Verification still needed."
    else:
        level, summary = "none", "No rule signals found. This is NOT proof the offer is genuine."
    return {"level": level, "summary": summary, "counts": n,
            "note": "Transparent rule-count indicator. Not a fraud probability."}
