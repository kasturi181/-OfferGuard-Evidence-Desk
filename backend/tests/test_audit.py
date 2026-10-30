import asyncio
import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import audit
from checks import site_age
from extract import extract_fields
from main import analyze_text
from rules import assess, run_rules

FEE = "Selected as Data Entry Executive at Northwind Tech Pvt Ltd, Pune. Joining date: 5th Nov 2026. Work from home. Salary Rs 85,000 per month. Pay a refundable registration fee of Rs 2,500. Contact hr.jobs@gmail.com"


def test_extracts_what_when_where():
    f = extract_fields(FEE)
    assert f["role"] == "Data Entry Executive" and f["start_date"] == "5th Nov 2026" and f["work_mode"] == "Work from home"


def test_missing_details_are_none_not_invented():
    f = extract_fields("Hi, interview Monday 10am. Details from hr@x.example")
    assert f["role"] is None and f["start_date"] is None and f["work_mode"] is None


def test_report_has_brief_audit_and_intel():
    r = asyncio.run(analyze_text(FEE))
    assert r["brief"]["state"] == "stop" and r["brief"]["headline"] == "Do not proceed"
    assert any("fee" in x.lower() for x in r["brief"]["risks_if_unverified"])
    assert r["audit"]["counts"]["triggered"] >= 2 and len(r["audit"]["rules"]) == 15
    assert any("No generative AI" in m for m in r["audit"]["method"])
    assert isinstance(r["intel"], list)


def test_audit_marks_rules_that_could_not_run():
    r = asyncio.run(analyze_text("Pay a refundable registration fee of Rs 2000"))
    st = {x["rule_id"]: x["status"] for x in r["audit"]["rules"]}
    assert st["RULE-01"] == "triggered"
    assert st["RULE-03"] == "could_not_run" and st["RULE-14"] == "could_not_run"   # no DB, no API key -> not evaluated
    assert st["RULE-06"] == "clear"


def test_vague_clean_message_is_not_called_safe():
    r = asyncio.run(analyze_text("Hi, we liked your profile. Please reply."))
    b = r["brief"]
    assert b["state"] == "verify" and "vague" in b["headline"].lower()
    assert "safe" not in (b["headline"] + b["subline"]).lower().replace("unsafe", "")


def test_rdap_parse_new_and_old():
    now = datetime(2026, 10, 30, tzinfo=timezone.utc)
    new = site_age.parse_rdap({"events": [{"eventAction": "registration", "eventDate": "2026-10-10T00:00:00Z"}]}, "x.example", now)
    old = site_age.parse_rdap({"events": [{"eventAction": "registration", "eventDate": "2010-01-01T00:00:00Z"}]}, "y.example", now)
    assert new["is_new"] and new["age_days"] == 20 and not old["is_new"]
    assert site_age.parse_rdap({}, "z.example", now)["status"] == "unavailable"


def test_age_check_statuses_and_rule15():
    new = {"domain": "x.example", "status": "ok", "registered": "2026-10-10", "age_days": 20, "registrar": None, "is_new": True}
    c = site_age.age_check([new])
    assert c["status"] == "warning"
    f = extract_fields("Hello")
    ids = [x["rule_id"] for x in run_rules("Hello", f, [c])]
    assert "RULE-15" in ids
    assert site_age.age_check([])["status"] == "not_checked"
    assert site_age.age_check([{"domain": "a.b", "status": "unavailable", "note": "n"}])["status"] == "unavailable"


def test_pick_domains_skips_personal_and_big_sites():
    f = {"url_domains": ["fake-jobs.example", "linkedin.com", "bit.ly"], "recruiter_emails": ["a@gmail.com", "b@corp.example"]}
    assert site_age.pick_domains(f) == ["fake-jobs.example", "corp.example"]


def test_decision_states():
    a = lambda lvl: {"level": lvl, "counts": {}}
    f = extract_fields(FEE)
    assert audit.build_brief(f, [], a("elevated"))["state"] == "pause"
    assert audit.build_brief(f, [], a("some"))["state"] == "verify"


def test_brief_uses_company_from_dataset_when_regex_misses():
    r = asyncio.run(analyze_text("Selected as Tester at Northwind Tech. Pay a refundable registration fee of Rs 500."))
    assert r["brief"]["facts"]["company"] == "Northwind Tech Pvt Ltd"


def test_monthly_pay_is_not_repeated():
    r = asyncio.run(analyze_text("Salary Rs 25,000 per month. Position of Tester."))
    assert "about" not in (r["brief"]["facts"]["pay"] or "")
