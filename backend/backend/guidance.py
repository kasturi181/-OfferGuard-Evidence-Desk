"""Actionable verification guidance (Innovation D). Static, deterministic."""
from __future__ import annotations

REPORT_PORTAL = "https://cybercrime.gov.in"
HELPLINE = "1930"
MCA_SEARCH = "https://www.mca.gov.in"


def build_guidance(fields: dict | None, verdict_key: str = "low_risk") -> dict:
    f = fields or {}
    company = (f.get("company_name") or "the company").strip()
    contact = [
        f"Search for {company} yourself and open its official website. Do not use links from the message.",
        "Find the HR or careers phone number or email on that official site. Call or write there, not to the recruiter's number.",
        "Ask HR to confirm the recruiter's name, the job title and the vacancy ID in writing.",
        "Check the company on the Ministry of Corporate Affairs site and compare name and registered address.",
    ]
    vacancy = [
        "Look for the same role on the official careers page or a verified LinkedIn company page.",
        "Real interviews are scheduled from a company email. Confirm the interviewer exists on the company page.",
        "Never pay for registration, training, uniform, laptop or security deposit to get a job.",
        "Share ID or bank documents only after a verified written offer and joining formalities.",
    ]
    report = [
        f"Report at {REPORT_PORTAL} or call {HELPLINE}. Keep screenshots, emails and payment receipts.",
        "If you paid, call your bank at once and ask to flag the transaction.",
        "Report the sender on the platform where you found the offer.",
    ]
    if verdict_key == "likely_fraudulent":
        contact.insert(0, "Stop replying to this sender until the company confirms the offer through its official channel.")
    return {
        "contact_employer": contact,
        "confirm_vacancy": vacancy,
        "report_fraud": report,
        "links": [{"label": "National Cyber Crime Reporting Portal", "url": REPORT_PORTAL},
                  {"label": "Ministry of Corporate Affairs", "url": MCA_SEARCH}],
        "helpline": HELPLINE,
    }
