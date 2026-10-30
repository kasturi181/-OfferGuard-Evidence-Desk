import sys, pathlib, asyncio
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from checklist import build_checklist
from checks.consistency import check_consistency
from checks.domain_age import check_domain_age
from checks.registry import check_registry
from verdict import compute_verdict
from guidance import build_guidance
from llm_explain import validate_extraction
from db_normalized import redact
import db_extra


def test_checklist_fee_is_now_priority():
    steps = build_checklist([{"title": "Upfront registration fee"}])
    assert steps[0]["priority"] == "now"


def test_checklist_empty_has_general_steps():
    assert len(build_checklist([])) == 3


def test_consistency_free_mail_mismatch():
    assert check_consistency({"company_name": "Acme Pvt Ltd", "emails": ["hr@gmail.com"]})[0]["status"] == "mismatch"


def test_consistency_match_keeps_unverified_note():
    r = check_consistency({"company_name": "Acme Pvt Ltd", "emails": ["hr@acme.com"]})[0]
    assert r["status"] == "match" and r["unverified"]


def test_consistency_missing_never_match():
    assert all(r["status"] == "not_checked" for r in check_consistency({}))


def test_cin_format():
    assert check_consistency({"registration_id": "U72900MH2015PTC123456"})[-1]["status"] == "match"
    assert check_consistency({"registration_id": "12345"})[-1]["status"] == "mismatch"


# ---- verdict ----
def test_strong_finding_is_likely_fraudulent_with_evidence():
    v = compute_verdict([{"title": "Upfront fee", "severity": "strong", "matched_text": "pay Rs 2000"}])
    assert v["verdict"] == "likely_fraudulent" and v["confidence"] == "high"
    assert v["basis"][0]["points"] == 40


def test_two_medium_is_suspicious():
    v = compute_verdict([{"title": "a", "severity": "medium"}, {"title": "b", "severity": "medium"}])
    assert v["verdict"] == "suspicious" and v["score"] == 30


def test_weak_only_is_low_risk_and_never_high_confidence():
    v = compute_verdict([{"title": "Telegram", "severity": "weak"}])
    assert v["verdict"] == "low_risk" and v["confidence"] == "limited"
    assert "not mean the offer is genuine" in v["summary"]


def test_consistency_mismatch_adds_points():
    v = compute_verdict([{"title": "a", "severity": "medium"}], [{"check": "x", "status": "mismatch"}])
    assert v["score"] == 23 and v["verdict"] == "suspicious"


def test_unavailable_check_lowers_confidence_and_is_listed():
    f = [{"title": "Upfront fee", "severity": "strong", "matched_text": "x"}]
    v = compute_verdict(f, [], [{"name": "URL reputation", "status": "unavailable"}])
    assert v["confidence"] == "moderate"
    assert any("URL reputation" in u for u in v["unverified"])


def test_verdict_always_has_disclaimer():
    assert "not a legal determination" in compute_verdict([])["disclaimer"]


def test_verdict_is_deterministic():
    f = [{"title": "a", "severity": "medium"}, {"title": "b", "severity": "weak"}]
    assert compute_verdict(f) == compute_verdict(f)


# ---- checks that must fail honestly ----
def test_domain_age_free_mail_not_checked():
    assert asyncio.run(check_domain_age("gmail.com"))["status"] == "not_checked"


def test_domain_age_simulated_failure_unavailable():
    assert asyncio.run(check_domain_age("example.com", simulate_failure=True))["status"] == "unavailable"


def test_registry_without_token_unavailable(monkeypatch):
    monkeypatch.delenv("OPENCORPORATES_API_TOKEN", raising=False)
    assert asyncio.run(check_registry("Acme Pvt Ltd"))["status"] == "unavailable"


# ---- LLM guard + privacy ----
def test_llm_extraction_drops_hallucinated_values():
    text = "Hi, Acme Corp is hiring. Mail hr@acme.com"
    out = validate_extraction({"company_name": "Acme Corp", "location": "Mars Base", "emails": ["hr@acme.com", "x@evil.com"]}, text)
    assert out == {"company_name": "Acme Corp", "emails": ["hr@acme.com"]}


def test_redact_removes_email_and_phone():
    r = redact("mail hr@acme.com call +91 98765 43210 ok")
    assert "@" not in r and "98765" not in r


def test_guidance_has_report_channel():
    g = build_guidance({"company_name": "Acme"}, "likely_fraudulent")
    assert g["helpline"] == "1930" and "Stop replying" in g["contact_employer"][0]


def test_summarize_counts_verdicts():
    rows = [{"created_at": "2026-10-29T10:00:00Z", "risk_level": "high", "verdict": "likely_fraudulent",
             "report": {"findings": [{"title": "Fee"}], "missing_checks": ["x"]}}]
    s = db_extra.summarize(rows)
    assert s["total"] == 1 and s["verdicts"]["likely_fraudulent"] == 1 and s["top_rules"][0]["rule"] == "Fee"
