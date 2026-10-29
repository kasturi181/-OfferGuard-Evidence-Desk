import asyncio, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from main import analyze_text

def ids(t):
    r = asyncio.run(analyze_text(t, simulate=True))
    return {f["rule_id"] for f in r["findings"]}, r

def test_fee():
    i, r = ids("Pay a refundable registration fee of ₹2,000 today.")
    assert "RULE-01" in i and r["assessment"]["level"] == "high"
    f = [x for x in r["findings"] if x["rule_id"] == "RULE-01"][0]
    assert r and f["evidence"] and f["start"] is not None

def test_otp():
    assert "RULE-02" in ids("Please share your OTP to confirm.")[0]

def test_domain_mismatch():
    i, r = ids("Offer from Northwind Tech Pvt Ltd. Contact hr@northwind-jobs.com")
    assert "RULE-04" in i

def test_domain_match_no_warning():
    i, r = ids("Offer from Northwind Tech Pvt Ltd. Contact hr@northwindtech.example")
    assert "RULE-04" not in i and any(c["status"] == "verified_match" for c in r["checks"])

def test_personal_email():
    assert "RULE-05" in ids("HR at Contoso Analytics Limited: contoso.hr@gmail.com")[0]

def test_docs_urgent_salary_redirect():
    i, _ = ids("Fresher data entry job, ₹90,000 per month, guaranteed job. Send your Aadhaar card now. Join Telegram group.")
    assert {"RULE-06", "RULE-07", "RULE-08", "RULE-09"} <= i

def test_benign_not_safe_claim():
    i, r = ids("Thanks for applying. Interview on Monday at 10am.")
    assert not (i - {"RULE-10"}) and "NOT proof" in r["assessment"]["summary"]

def test_unavailable_url_marked():
    _, r = ids("Apply at https://example.com/apply")
    c = [c for c in r["checks"] if c["name"] == "url_reputation"][0]
    assert c["status"] == "unavailable"
