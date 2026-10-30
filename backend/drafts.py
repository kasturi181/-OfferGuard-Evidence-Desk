"""Ready-to-send messages built from what was found. Placeholders stay in [brackets]."""
from checks.company_identity import norm


def _rec(text: str, companies: list[dict]):
    t = norm(text)
    return next((r for r in companies if norm(r["name"]) in t), None)


def build_drafts(text: str, fields: dict, findings: list[dict], companies: list[dict]) -> list[dict]:
    rec = _rec(text, companies)
    company = (rec or {}).get("name") or fields.get("company") or "[company name]"
    ids = {f["rule_id"] for f in findings}
    dom = ((rec or {}).get("official_domains") or [None])[0]
    careers = (rec or {}).get("careers_url")
    out = []

    asks = [
        f"Your full name, designation and an email address on the company's official domain{f' (@{dom})' if dom else ''}.",
        f"The link to this vacancy on the company's official careers page{f' ({careers})' if careers else ''}.",
        "The company's registered name, CIN and registered office address.",
        "Written confirmation that no fee or deposit is needed at any stage.",
        "The name of the hiring manager and the HR phone number listed on the company's website.",
    ]
    body = (f"Hello,\n\nThank you for the opportunity with {company}. Before I go further, I would like to verify the offer through official channels. "
            "Could you please share:\n" + "\n".join(f"{i}. {a}" for i, a in enumerate(asks, 1)) +
            "\n\nI will check these on the company's official website and the MCA portal. Until then I will not make any payment or share OTPs or documents.\n\nRegards,\n[Your name]")
    out.append({"title": "Message to the recruiter", "hint": "Send this before you do anything else. A genuine recruiter will answer easily.", "text": body})

    if rec or fields.get("company"):
        contact = ", ".join(fields.get("recruiter_emails", [])[:2] + fields.get("phones", [])[:1]) or "[recruiter contact]"
        links = ", ".join(fields.get("url_domains", [])[:2]) or "none"
        pay = " The person also asked for a payment or fee." if "RULE-01" in ids else ""
        out.append({
            "title": "Message to the company's official HR",
            "hint": "Send it to the contact listed on the company's own website, not to the details in the offer.",
            "text": (f"Hello {company} HR team,\n\nI received a job offer from someone using {contact}. Links in the message: {links}.{pay}\n\n"
                     "Could you please confirm whether this person and this vacancy are genuine?\n\nThank you,\n[Your name]"),
        })

    if any(f["severity"] in ("strong", "medium") for f in findings):
        asked = "; ".join(f["evidence"][:120] for f in findings if f["rule_id"] in ("RULE-01", "RULE-02", "RULE-06")) or "[what they asked for]"
        out.append({
            "title": "Notes for a cybercrime report",
            "hint": "Copy into the form at cybercrime.gov.in, or tell them when you call 1930. Fill the [brackets].",
            "text": (f"Date and time: [date]\nCompany claimed: {company}\nRecruiter contact: {', '.join(fields.get('recruiter_emails', []) + fields.get('phones', [])) or '[contact]'}\n"
                     f"Links: {', '.join(fields.get('urls', [])) or 'none'}\nWhat they asked for: {asked}\nHow they contacted me: [email / WhatsApp / SMS / call]\n"
                     "Money paid (if any): [amount]\nTransaction ID / UPI ID: [id]\nScreenshots saved: [yes/no]"),
        })
    return out
