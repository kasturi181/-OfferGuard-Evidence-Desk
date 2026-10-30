"""Deterministic rules. No FastAPI, no network. Same logic everywhere."""
import re
from extract import PAYMENT

PERSONAL = ("gmail.com", "yahoo.com", "yahoo.in", "outlook.com", "hotmail.com", "rediffmail.com", "proton.me", "protonmail.com")
NEG = re.compile(r"\b(?:no|not|never|without|zero|free of)\b[^.\n]{0,30}$", re.I)
LOW_SKILL = re.compile(r"\b(fresher|intern(?:ship)?|data entry|typing|part[- ]time|work from home|wfh|form filling)\b", re.I)

CRED = re.compile(r"(?:share|send|provide|give|tell|enter)[^.\n]{0,40}\b(?:otp|password|pin|cvv|upi pin|net ?banking|card number|bank (?:login|credentials))\b[^.\n]{0,20}", re.I)
DOCS = re.compile(r"(?:send|share|submit|upload|provide)[^.\n]{0,50}\b(?:aadhaar|aadhar|pan card|passport|bank (?:account|statement|details)|passbook|cancelled cheque)\b[^.\n]{0,20}", re.I)
URGENT = re.compile(r"(?:guaranteed (?:job|selection|placement)|100%\s*(?:selection|placement|job)|confirmed selection|within \d+\s*(?:hours?|minutes?)|last chance|today only|limited (?:seats|slots)|act (?:now|immediately)|respond immediately)[^.\n]{0,30}", re.I)
REDIRECT = re.compile(r"(?:telegram|whatsapp)[^.\n]{0,50}|(?:wa\.me|t\.me|forms\.gle|bit\.ly|docs\.google\.com/forms)/\S+", re.I)

LIMITS = [
    "Warning signals are not proof of fraud. Absence of signals is not proof of safety.",
    "A company-record match shows an entity may exist; it does not prove the recruiter is authorized.",
    "Company records come from a small synthetic sample dataset, not an official registry.",
    "Scanned PDFs are not read directly. Upload a screenshot of the page or paste the text instead.",
    "Community signals come from unverified user reports and earlier high-risk checks. They can be wrong or malicious.",
]


def _f(rule_id, severity, title, claim, text, m, why, action, status="matched_rule", unc="Text observation only; context outside the message is unknown."):
    return {
        "rule_id": rule_id, "severity": severity, "title": title, "claim": claim,
        "evidence": m.group(0).strip() if m else text, "start": m.start() if m else None,
        "end": m.end() if m else None, "source": "User-provided message", "why": why,
        "status": status, "uncertainty": unc, "action": action,
    }


def run_rules(text: str, fields: dict, checks: list[dict], consistency: list[dict] | None = None) -> list[dict]:
    out = []
    if m := next((x for x in PAYMENT.finditer(text) if not NEG.search(text[max(0, x.start() - 35):x.start()])), None):
        out.append(_f("RULE-01", "strong", "Upfront payment request", "The message asks the candidate to pay before securing the job.", text, m,
                      "Upfront recruitment fees are a common warning sign and warrant independent verification.", "Do not pay until the opportunity is verified through the company's official channels."))
    if m := CRED.search(text):
        out.append(_f("RULE-02", "strong", "Credential / OTP request", "The message asks for OTP, password, PIN or banking credentials.", text, m,
                      "Legitimate hiring does not need OTPs, PINs or passwords.", "Never share credentials. Stop replying and report to the platform you found it on."))
    def chk(name):
        return next((c for c in checks if c["name"] == name), None)

    def from_check(rule_id, severity, title, claim, c, why, action, unc):
        return {"rule_id": rule_id, "severity": severity, "title": title, "claim": claim, "evidence": c["details"], "start": None, "end": None,
                "source": f"{c['source']} (checked {c['checked_at']})", "why": why, "status": "warning", "uncertainty": unc, "action": action}

    if (c := chk("url_reputation")) and c["status"] == "warning":
        out.append(from_check("RULE-03", "strong", "URL on reputation threat list", "A link in the message is flagged by a reputation provider.", c,
                              "Flagged URLs may host phishing or malware. Advisory data: Google Safe Browsing.", "Do not open the link.", "Provider lists can contain errors; treat as potential risk."))
    if (c := chk("email_domain_consistency")) and c["status"] == "warning":
        out.append(from_check("RULE-04", "medium", "Recruiter domain inconsistent with company record", "Recruiter email domain differs from the known official domain.", c,
                              "Real companies can be impersonated with look-alike domains.", "Find the company's official careers page yourself and confirm the recruiter there.",
                              "Mismatch means unverified, not proven fraud. Companies may use other domains."))
    if (c := chk("link_domain_consistency")) and c["status"] == "warning":
        out.append(from_check("RULE-11", "medium", "Link points away from the company's domain", "A link in the offer does not belong to the company's known domain.", c,
                              "Look-alike links are used to collect documents or money.", "Do not use the link. Open the official careers page yourself.", "Companies sometimes use third-party hiring portals."))
    if (c := chk("registration_id_consistency")) and c["status"] == "warning":
        out.append(from_check("RULE-12", "medium", "Registration ID differs from the record", "The CIN in the offer does not match the dataset record for this company.", c,
                              "A wrong registration number suggests a copied or invented identity.", "Verify the CIN on the MCA portal.", "The dataset may be outdated or incomplete."))
    if (c := chk("location_consistency")) and c["status"] == "warning":
        out.append(from_check("RULE-13", "weak", "Location differs from the record", "The offer mentions a city different from the recorded head office.", c,
                              "A weak signal on its own.", "Ask where the job is based and confirm on the official website.", "Companies often have several offices."))
    if (c := chk("community_reports")) and c["status"] == "warning":
        out.append(from_check("RULE-14", "medium" if c.get("count", 0) >= 3 else "weak", "Matches reports from other users", "Some details match reports or earlier high-risk checks from other people.", c,
                              "Independent reports are a reason to verify more carefully.", "Verify through official channels before proceeding.",
                              "Reports are unverified and could be mistaken or malicious."))
    if (c := chk("domain_age")) and c["status"] == "warning":
        out.append(from_check("RULE-15", "weak", "Website was registered very recently", "A website in the offer is less than 90 days old.", c,
                              "Scam sites are often created days before a campaign. A new site alone proves nothing.", "Find the company's official website yourself and compare.",
                              "New companies and new hiring campaigns also have new websites."))
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
    for it in consistency or []:
        if it["status"] == "warning" and it["field"] in ("Links", "Registration ID"):
            rid, title = ("RULE-11", "Link domain not consistent with company record") if it["field"] == "Links" else ("RULE-12", "Registration ID differs from company record")
            out.append({"rule_id": rid, "severity": "medium", "title": title, "claim": f"{it['field']} in the message does not match the reference record.",
                        "evidence": f"Claimed: {it['claimed']} | Reference: {it['reference']}", "start": None, "end": None, "source": "Synthetic sample dataset (NOT an official registry)",
                        "why": it["note"], "status": "warning", "uncertainty": "Mismatch means unverified, not proven fraud. The sample dataset is tiny.",
                        "action": "Verify independently on the official website and the MCA portal."})
    ci = chk("company_identity")
    if (not ci) or ci["status"] in ("not_checked", "unavailable"):
        out.append({"rule_id": "RULE-10", "severity": "info", "title": "Company / recruiter not independently verified", "claim": "No source confirms the company or the recruiter's authority.",
                    "evidence": ci["details"] if ci else "No company check ran.", "start": None, "end": None, "source": "OfferGuard checks", "why": "Missing evidence is not evidence of safety.",
                    "status": "unavailable", "uncertainty": "Sample dataset is tiny; absence here means little.", "action": "Verify the company on the MCA portal and the recruiter via the official website."})
    order = {"strong": 0, "medium": 1, "weak": 2, "info": 3}
    return sorted(out, key=lambda f: (order[f["severity"]], f["rule_id"]))


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


_ORDER = {"now": 0, "soon": 1, "later": 2}


def build_checklist(findings: list[dict]) -> list[dict]:
    ids = {f["rule_id"] for f in findings}
    out = []

    def add(p, t, d):
        out.append({"priority": p, "title": t, "detail": d})

    if "RULE-01" in ids:
        add("now", "Do not pay any fee", "Genuine employers do not usually ask candidates to pay to get a job. If you already paid, contact your bank and report quickly at cybercrime.gov.in or helpline 1930.")
    if "RULE-02" in ids:
        add("now", "Protect your accounts", "If you shared an OTP, PIN or password, contact your bank immediately, change passwords and block the card or UPI handle if needed.")
    if "RULE-03" in ids:
        add("now", "Do not open the flagged link", "A reputation service lists it as potentially harmful. Do not enter details on that page.")
    if "RULE-06" in ids:
        add("soon", "Hold back identity documents", "Share Aadhaar, PAN, passport or bank details only after you have verified the employer and received a formal offer.")
    if ids & {"RULE-04", "RULE-05", "RULE-11"}:
        add("soon", "Confirm the recruiter on the official site", "Type the company's website address yourself, find its careers or contact page, and email or call the listed HR contact to confirm this person and vacancy.")
    if "RULE-08" in ids:
        add("soon", "Compare the salary", "Check pay for the same role on trusted job boards. Pay far above market for an entry-level job is a common lure.")
    if "RULE-07" in ids:
        add("soon", "Take your time", "Pressure and guaranteed selection reduce your time to verify. A real employer will allow time.")
    if "RULE-09" in ids:
        add("later", "Move to official channels", "Prefer the company's own application portal or official email over chat apps and external forms.")
    add("soon", "Verify the company exists", "Look up the company's registration on the MCA portal (mca.gov.in) and check it has a real website and a visible presence.")
    add("later", "Confirm the vacancy", "Check the role is listed on the company's own careers page or a trusted job board.")
    add("later", "Report suspected fraud", "Report at cybercrime.gov.in (helpline 1930 for financial fraud) and flag the listing on the platform where you found it.")
    return sorted(out, key=lambda x: _ORDER[x["priority"]])
