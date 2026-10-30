"""Tailored safety checklist. Pure function, no network, no FastAPI.

build_checklist(findings, fields) -> list of steps:
    {"id", "priority": "now"|"next"|"always", "action", "why", "trigger"}
Matching is keyword based on the finding text, so it works with whatever
keys your rules.py puts in a finding (rule / id / title / claim ...).
"""
from __future__ import annotations

REPORT_LINKS = {
    "cybercrime_portal": "https://cybercrime.gov.in",
    "helpline": "1930",
}

# (keywords, priority, action, why)
_RULES = [
    (("fee", "registration", "processing", "security deposit", "upfront"),
     "now",
     "Do not pay anything. Real employers do not charge to give you a job.",
     "Upfront payment for a job is the strongest scam signal."),
    (("otp", "password", "pin", "banking credential", "cvv"),
     "now",
     "Never share an OTP, PIN or password. Stop replying to this sender.",
     "OTP/credential requests give attackers direct access to your accounts."),
    (("url flagged", "safe browsing", "reputation", "malicious url", "threat"),
     "now",
     "Do not open the flagged link. If you already did, change passwords on accounts you used.",
     "The link matched a known threat list."),
    (("domain", "inconsistent", "mismatch"),
     "next",
     "Find the company's official website yourself (search the name, do not use the link in the message) and compare the email domain.",
     "Recruiter email domain does not match the company."),
    (("personal email", "gmail", "yahoo", "outlook", "hotmail"),
     "next",
     "Ask for an email from the company's own domain and confirm it on the official careers page.",
     "Corporate hiring from a free mailbox is a medium signal."),
    (("sensitive", "aadhaar", "pan", "bank", "passport", "identity", "document"),
     "next",
     "Do not send ID or bank documents before a verified interview and written offer.",
     "Early document requests are used for identity theft."),
    (("guaranteed", "urgent", "immediately", "time pressure", "limited seats"),
     "next",
     "Take your time. Ask the recruiter for the vacancy ID and verify it with the company.",
     "Pressure tactics try to stop you from checking."),
    (("salary", "implausible", "unrealistic"),
     "next",
     "Compare the pay with similar roles on trusted job boards.",
     "Pay far above market for an entry role is a common lure."),
    (("telegram", "whatsapp", "external form", "google form"),
     "next",
     "Move the conversation to official email or the company portal.",
     "Moving to chat apps avoids a verifiable paper trail."),
    (("not independently verified", "unverified", "not verified"),
     "next",
     "Verify the company on MCA (mca.gov.in) and call the number listed on its official website.",
     "No independent record was matched in this check."),
]

_ALWAYS = [
    ("always",
     "Contact the employer through a trusted channel: phone number or HR email from the official website, not from the message.",
     "This is the only way to confirm the vacancy exists."),
    ("always",
     "Search the company name with the word 'scam' or 'fake offer' and read recent results.",
     "Others may already have reported it."),
    ("always",
     "If you suspect fraud, report at cybercrime.gov.in or call 1930 (India) and keep screenshots.",
     "Reports help police and other job seekers."),
]


def _text_of(finding) -> str:
    if isinstance(finding, dict):
        return " ".join(str(v) for v in finding.values()).lower()
    return str(finding).lower()


def build_checklist(findings, fields=None) -> list[dict]:
    steps: list[dict] = []
    seen: set[str] = set()
    for f in findings or []:
        text = _text_of(f)
        label = (f.get("title") or f.get("rule") or f.get("claim") or "signal") if isinstance(f, dict) else "signal"
        for keys, prio, action, why in _RULES:
            if any(k in text for k in keys) and action not in seen:
                seen.add(action)
                steps.append({"id": f"s{len(steps)+1}", "priority": prio,
                              "action": action, "why": why, "trigger": str(label)})
    order = {"now": 0, "next": 1, "always": 2}
    steps.sort(key=lambda s: order[s["priority"]])
    for prio, action, why in _ALWAYS:
        steps.append({"id": f"s{len(steps)+1}", "priority": prio,
                      "action": action, "why": why, "trigger": "general"})
    return steps
