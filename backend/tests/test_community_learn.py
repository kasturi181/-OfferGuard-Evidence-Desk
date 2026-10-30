import asyncio
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import db
from checks import community
from learn import signals_from
from rules import run_rules


def _f(rule_id):
    return {"rule_id": rule_id}


FIELDS = {"recruiter_emails": ["pay.now@gmail.com", "hr@fake-jobs.example"], "url_domains": ["fake-jobs.example", "linkedin.com", "bit.ly"],
          "phones": ["9000000009"], "company": None}


def test_learns_only_after_strong_text_rule():
    assert signals_from(FIELDS, [_f("RULE-09")], []) == []
    got = signals_from(FIELDS, [_f("RULE-01")], [])
    assert ("email", "pay.now@gmail.com") in got and ("domain", "fake-jobs.example") in got and ("phone", "9000000009") in got


def test_never_learns_big_sites_or_verified_company_domains():
    got = signals_from(FIELDS, [_f("RULE-01")], [{"official_domains": ["fake-jobs.example"]}])
    values = {v for _, v in got}
    assert "linkedin.com" not in values and "bit.ly" not in values and "fake-jobs.example" not in values


def _run(rows, monkeypatch, fields=FIELDS):
    async def fake(values):
        return "ok", rows
    monkeypatch.setattr(db, "find_scam_reports", fake)
    return asyncio.run(community.check_community(fields))


def test_single_auto_signal_is_ignored(monkeypatch):
    rows = [{"kind": "phone", "value": "9000000009", "source": "auto", "reporter": "ip:a"}]
    assert _run(rows, monkeypatch)["status"] == "no_match"


def test_two_different_reporters_show_signal(monkeypatch):
    rows = [{"kind": "phone", "value": "9000000009", "source": "auto", "reporter": "ip:a"},
            {"kind": "phone", "value": "9000000009", "source": "auto", "reporter": "ip:b"}]
    r = _run(rows, monkeypatch)
    assert r["status"] == "warning" and r["count"] == 2 and "earlier high-risk checks" in r["details"]


def test_user_report_counts_immediately_and_old_rows_without_source_work(monkeypatch):
    rows = [{"kind": "domain", "value": "fake-jobs.example", "description": "x"}]  # pre-migration row: no source column
    r = _run(rows, monkeypatch)
    assert r["status"] == "warning" and r["count"] == 1


def test_three_matches_raise_severity_to_medium(monkeypatch):
    rows = [{"kind": "domain", "value": "fake-jobs.example", "source": "user", "reporter": f"ip:{i}"} for i in range(3)]
    c = _run(rows, monkeypatch)
    fields = {**FIELDS, "salaries": [], "payment_phrases": [], "registration_ids": [], "cities": []}
    findings = run_rules("Hello", fields, [c])
    rule14 = next(f for f in findings if f["rule_id"] == "RULE-14")
    assert rule14["severity"] == "medium"
    c1 = {**c, "count": 1}
    assert next(f for f in run_rules("Hello", fields, [c1]) if f["rule_id"] == "RULE-14")["severity"] == "weak"


def test_db_disabled_is_not_checked(monkeypatch):
    async def fake(values):
        return "disabled", []
    monkeypatch.setattr(db, "find_scam_reports", fake)
    assert asyncio.run(community.check_community(FIELDS))["status"] == "not_checked"
