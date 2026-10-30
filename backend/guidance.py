"""Tailored, practical next steps based on what was detected."""

TAILORED = {
    "RULE-01": ("Do not pay anything", ["Do not pay any registration, training or security fee to get a job.", "Real employers do not charge candidates to hire them.", "If you already paid: call 1930 (national cybercrime helpline) now and report at cybercrime.gov.in. Keep payment proof."]),
    "RULE-02": ("Protect your accounts", ["Never share OTP, PIN, CVV or passwords with a recruiter.", "If you already did: call your bank immediately, block the card/UPI and change passwords. Then call 1930."]),
    "RULE-03": ("Do not open the flagged link", ["Close the link. If you opened it, do not enter any details.", "Run a device scan and change passwords if you typed any."]),
    "RULE-04": ("Check the recruiter's email domain", ["Ask for an email from the company's own domain.", "Type the company website yourself and compare the domain letter by letter."]),
    "RULE-05": ("Ask for a company email", ["Ask the recruiter to write from a company-domain email.", "Confirm the recruiter's name on the company's official site or LinkedIn."]),
    "RULE-06": ("Hold back identity documents", ["Do not send Aadhaar, PAN, passport or bank details before a verified offer.", "If you already shared them, watch for misuse and report suspicious activity."]),
    "RULE-07": ("Slow down", ["Guaranteed selection and tight deadlines are pressure tactics. Take a day and verify."]),
    "RULE-08": ("Check the salary against the market", ["Compare with similar roles on trusted job boards. Pay far above market for entry-level work is a common lure."]),
    "RULE-09": ("Move to official channels", ["Apply only through the company's official careers page.", "Be careful with Telegram/WhatsApp groups and Google Forms asking for money or documents."]),
    "RULE-11": ("Check the link's website", ["Do not use links from the message. Search for the company yourself and open its official careers page."]),
    "RULE-12": ("Verify the registration number", ["Look the company up on the MCA portal (mca.gov.in, Company/LLP master data) and compare the CIN with the one in the offer."]),
    "RULE-13": ("Confirm the office location", ["Ask where the job is based. Companies can have many offices, so confirm on the official website."]),
    "RULE-14": ("Others reported matching details", ["Other users reported some of the same details. These reports are unverified, so treat them as a reason to verify, not as proof."]),
}
BASE = [
    ("Find the employer yourself", ["Search for the company's official website yourself, not through links in the message.", "Check that the same vacancy is listed on its careers page.", "Call the phone number on the official website, not the one in the message."]),
    ("Check the company exists", ["Search the company on the MCA portal (mca.gov.in) and compare name and CIN.", "Look at its LinkedIn page: history, employees, recent posts."]),
]
REPORT = ("Report it", ["Report at cybercrime.gov.in or call 1930.", "Report the post or account to the job platform.", "Keep screenshots, chats and payment proof."])


def build_checklist(findings: list[dict]) -> list[dict]:
    ids = {f["rule_id"] for f in findings}
    out = [{"title": t, "steps": s, "tied_to": rid} for rid, (t, s) in TAILORED.items() if rid in ids]
    out += [{"title": t, "steps": s, "tied_to": None} for t, s in BASE]
    if any(f["severity"] in ("strong", "medium") for f in findings):
        out.append({"title": REPORT[0], "steps": REPORT[1], "tied_to": None})
    return out
