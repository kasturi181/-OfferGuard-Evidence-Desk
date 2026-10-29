import io
import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
URL = re.compile(r"(?:https?://|www\.)[^\s<>\"')]+|(?:wa\.me|t\.me|bit\.ly|forms\.gle)/[^\s<>\"')]+", re.I)
COMPANY = re.compile(
    r"((?:[A-Z][\w&\-]*\s){1,4}(?:Pvt\.?\s*Ltd\.?|Private Limited|Limited|Ltd\.?|LLP|Inc\.?|Technologies|Solutions|Systems|Labs))"
)
SALARY = re.compile(
    r"(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)\s*(k|lakhs?|lpa)?\s*(?:/|per\s*|a\s*)?(month|mo|day|week|year|annum|pm|lpa)?",
    re.I,
)
PAYMENT = re.compile(
    r"(?:(?:pay|deposit|transfer|send|submit)[^.\n]{0,60}?(?:registration|processing|security|training|joining|refundable|kit|verification)[^.\n]{0,25}?(?:fee|fees|charges?|deposit|amount))"
    r"|(?:(?:registration|processing|security|joining|training|refundable)\s+(?:fee|fees|charges?|deposit)[^.\n]{0,40})",
    re.I,
)


def monthly_inr(amount: float, unit: str | None, period: str | None) -> float:
    unit, period = (unit or "").lower(), (period or "").lower()
    if unit == "k":
        amount *= 1_000
    elif unit.startswith("lakh") or unit == "lpa":
        amount *= 100_000
    if unit == "lpa" or period in ("year", "annum", "lpa"):
        return amount / 12
    if period == "day":
        return amount * 26
    if period == "week":
        return amount * 4
    return amount


def extract_fields(text: str) -> dict:
    company = COMPANY.search(text)
    salaries = []
    for m in SALARY.finditer(text):
        try:
            amt = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        salaries.append(
            {"raw": m.group(0).strip(), "monthly_inr": round(monthly_inr(amt, m.group(2), m.group(3))),
             "period": (m.group(3) or "month").lower(), "start": m.start(), "end": m.end()}
        )
    return {
        "company": company.group(1).strip() if company else None,
        "recruiter_emails": list(dict.fromkeys(EMAIL.findall(text))),
        "urls": list(dict.fromkeys(u.rstrip(".,;") for u in URL.findall(text))),
        "salaries": salaries,
        "payment_phrases": [m.group(0).strip() for m in PAYMENT.finditer(text)],
    }


def pdf_to_text(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return "\n".join((p.extract_text() or "") for p in reader.pages).strip()
