"""Offer brief + audit trail. Deterministic. No network, no AI.

brief : what the offer says (role, company, place, start, pay) and what to do (stop / pause / verify), plus the risk
        you take if you proceed without verifying.
audit : every rule that was evaluated (triggered / clear / could not run), every check, and how the result was made.
"""
from datetime import datetime, timezone

ENGINE = "OfferGuard deterministic rules, 2026-10"

RULES = {
    "RULE-01": "Upfront payment request", "RULE-02": "OTP / credentials request", "RULE-03": "Link flagged by Google Safe Browsing",
    "RULE-04": "Recruiter email domain differs from company record", "RULE-05": "Personal email used for corporate hiring",
    "RULE-06": "Identity / bank documents requested early", "RULE-07": "Guaranteed selection or time pressure",
    "RULE-08": "Implausible salary for an entry-level role", "RULE-09": "Redirect to chat app or external form",
    "RULE-10": "Company / recruiter not independently verified", "RULE-11": "Link domain differs from company record",
    "RULE-12": "Registration ID (CIN) differs from record", "RULE-13": "Location differs from company record",
    "RULE-14": "Details match user reports or earlier high-risk checks", "RULE-15": "Website registered very recently",
}
# rules that depend on an external check; if that check did not run, the rule could not be evaluated
NEEDS = {"RULE-03": ("url_reputation", {"warning", "no_match", "verified_match"}),
         "RULE-04": ("email_domain_consistency", {"warning", "verified_match"}),
         "RULE-11": ("link_domain_consistency", {"warning", "verified_match"}),
         "RULE-12": ("registration_id_consistency", {"warning", "verified_match"}),
         "RULE-13": ("location_consistency", {"warning", "verified_match"}),
         "RULE-14": ("community_reports", {"warning", "no_match"}),
         "RULE-15": ("domain_age", {"warning", "no_match"})}

RISK = {
    "RULE-01": "Money: you may lose the fee and never get a job.",
    "RULE-02": "Bank and accounts: sharing an OTP, PIN or password can empty your account.",
    "RULE-06": "Identity: Aadhaar, PAN or bank details can be used for loans or fraud in your name.",
    "RULE-03": "Device and logins: the link may steal passwords or install malware.",
    "RULE-04": "Impersonation: you may be talking to someone pretending to be the company.",
    "RULE-11": "Impersonation: the link may be a look-alike of the real company site.",
    "RULE-05": "Impersonation: anyone can open a free mailbox and claim to be a recruiter.",
    "RULE-12": "Fake identity: the registration number does not match the company.",
}
CORE = [("company", "Company"), ("role", "Role"), ("location", "Location"), ("start", "Start date"), ("pay", "Pay"), ("contact", "Recruiter contact")]


def _facts(f: dict) -> dict:
    sal = f.get("salaries") or []
    contact = (f.get("recruiter_emails") or [])[:2] + (f.get("phones") or [])[:1]
    return {
        "company": f.get("company"), "role": f.get("role"),
        "location": ", ".join(c.title() for c in f.get("cities") or []) or None,
        "start": f.get("start_date"), "mode": f.get("work_mode"),
        "pay": (sal[0]["raw"] if sal[0]["period"] == "month" else f"{sal[0]['raw']} (about ₹{sal[0]['monthly_inr']:,} per month)") if sal else None,
        "contact": ", ".join(contact) or None,
    }


def build_brief(fields: dict, findings: list[dict], assessment: dict) -> dict:
    facts = _facts(fields)
    stated = [k for k, _ in CORE if facts.get(k)]
    missing = [label for k, label in CORE if not facts.get(k)]
    ids = {x["rule_id"] for x in findings}
    level = assessment["level"]
    top = [x["title"] for x in findings if x["severity"] in ("strong", "medium")][:4]

    if level == "high":
        state, head, sub = "stop", "Do not proceed", "Do not pay money, share documents or share any OTP. Verify the employer through its official website first."
    elif level == "elevated":
        state, head, sub = "pause", "Pause and verify first", "Several warning signs. Do not pay or share documents until the employer confirms this offer through an official channel."
    elif level == "some":
        state, head, sub = "verify", "Verify before you proceed", "Some warning signs were found. Check them, then decide."
    elif len(stated) <= 2:
        state, head, sub = "verify", "Too vague to judge", "The message gives almost no concrete details. Ask for a written offer before you decide."
    else:
        state, head, sub = "verify", "No known red flags. That is not proof.", "Our rules found nothing alarming, but we could not confirm the company or recruiter. Verify before you accept."

    risks = [RISK[r] for r in ("RULE-01", "RULE-02", "RULE-06", "RULE-03", "RULE-04", "RULE-11", "RULE-05", "RULE-12") if r in ids]
    if not risks:
        risks = ["Time: accepting an unverified offer can waste weeks, and fake employers often ask for money or documents later."]
    must = ["Company exists on the MCA portal and the recruiter works there (ask HR on the company's official number).",
            "The same vacancy is on the company's own careers page.",
            "Pay, role, location and start date are in a written offer sent from a company email."]
    if ids & {"RULE-04", "RULE-11"}:
        must.insert(0, "The email and link domains match the company's real website (type the address yourself).")
    return {
        "state": state, "headline": head, "subline": sub, "because": top,
        "facts": facts,
        "completeness": {"stated": len(stated), "total": len(CORE), "missing": missing,
                         "note": "A genuine offer normally names the company, role, place, start date and pay."},
        "risks_if_unverified": risks, "must_verify": must,
        "upside_note": "We cannot judge whether the job itself is good (pay, growth, fit). That part is your decision. We only check whether the offer looks real.",
    }


def build_audit(text: str, fields: dict, findings: list[dict], checks: list[dict], missing: list[str], limits: list[str]) -> dict:
    hit = {f["rule_id"]: f for f in findings}
    status = {c["name"]: c["status"] for c in checks}
    rules = []
    for rid, title in RULES.items():
        if rid in hit:
            st = "triggered"
        elif rid in NEEDS and status.get(NEEDS[rid][0]) not in NEEDS[rid][1]:
            st = "could_not_run"
        else:
            st = "clear"
        rules.append({"rule_id": rid, "title": title, "status": st, "severity": hit[rid]["severity"] if rid in hit else None})
    return {
        "engine": ENGINE,
        "analyzed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "method": [
            "Details are extracted from the text with regular expressions (no AI).",
            f"{len(RULES)} fixed rules are evaluated on the text and on the check results below.",
            "The risk level is a rule count: any strong sign = high; 2+ medium = elevated; any other sign = some. It is not a probability.",
            "Screenshots are read on your device with OCR before analysis. No generative AI decides anything here.",
        ],
        "input": {"characters": len(text), "links": len(fields.get("urls") or []), "emails": len(fields.get("recruiter_emails") or []),
                  "phones": len(fields.get("phones") or [])},
        "rules": rules,
        "counts": {"triggered": sum(r["status"] == "triggered" for r in rules), "clear": sum(r["status"] == "clear" for r in rules),
                   "could_not_run": sum(r["status"] == "could_not_run" for r in rules)},
        "checks": [{"name": c["name"], "status": c["status"], "source": c["source"], "checked_at": c["checked_at"]} for c in checks],
        "not_checked": missing, "limits": limits,
    }
