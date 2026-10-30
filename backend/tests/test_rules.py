import asyncio, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from main import analyze_text


def run(t):
    r = asyncio.run(analyze_text(t, simulate=True))
    return {f["rule_id"] for f in r["findings"]}, r


def test_fee():
    i, r = run("Pay a refundable registration fee of ₹2,000 today.")
    assert "RULE-01" in i and r["assessment"]["level"] == "high"
    f = [x for x in r["findings"] if x["rule_id"] == "RULE-01"][0]
    assert f["evidence"] and f["start"] is not None
    assert r["extracted_fields"]["salaries"] == []  # fee is not a salary


def test_otp():
    assert "RULE-02" in run("Please share your OTP to confirm.")[0]


def test_domain_mismatch():
    assert "RULE-04" in run("Offer from Northwind Tech Pvt Ltd. Contact hr@northwind-jobs.com")[0]


def test_domain_match_no_warning():
    i, r = run("Offer from Northwind Tech Pvt Ltd. Contact hr@northwindtech.example")
    names = {c["name"]: c["status"] for c in r["checks"]}
    assert "RULE-04" not in i and names["company_identity"] == "verified_match" and names["email_domain_consistency"] == "verified_match"


def test_personal_email():
    assert "RULE-05" in run("HR at Contoso Analytics Limited: contoso.hr@gmail.com")[0]


def test_docs_urgent_salary_redirect():
    i, _ = run("Fresher data entry job, ₹90,000 per month, guaranteed job. Send your Aadhaar card now. Join Telegram group.")
    assert {"RULE-06", "RULE-07", "RULE-08", "RULE-09"} <= i


def test_benign_not_safe_claim():
    i, r = run("Thanks for applying. Interview on Monday at 10am.")
    assert not (i - {"RULE-10"}) and "NOT proof" in r["assessment"]["summary"]


def test_unavailable_url_marked():
    _, r = run("Apply at https://example.com/apply")
    assert [c for c in r["checks"] if c["name"] == "url_reputation"][0]["status"] == "unavailable"


def test_link_mismatch():
    assert "RULE-11" in run("Northwind Tech Pvt Ltd. Apply at https://northwind-careers.com/apply from hr@northwindtech.example")[0]


def test_cin_mismatch_and_match():
    assert "RULE-12" in run("Northwind Tech Pvt Ltd CIN U11111MH2000PTC000001, hr@northwindtech.example")[0]
    i, r = run("Northwind Tech Pvt Ltd CIN U72900KA2015PTC123456, hr@northwindtech.example")
    assert "RULE-12" not in i


def test_location_mismatch():
    assert "RULE-13" in run("Northwind Tech Pvt Ltd. Job location: Pune. hr@northwindtech.example")[0]


def test_checklist_tailored():
    _, r = run("Pay a refundable registration fee of Rs 500")
    titles = [c["title"] for c in r["checklist"]]
    assert "Do not pay anything" in titles and "Report it" in titles
