import sys, pathlib, asyncio
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from datetime import datetime, timezone, timedelta
from checks import live
from extract import extract_fields
from rules import run_rules


def cin_check(text):
    return live.check_cin(text, extract_fields(text))


def test_cin_valid_decodes():
    c = cin_check("Northwind Tech Pvt Ltd CIN U72900KA2015PTC123456")[0]
    assert c["status"] == "no_match" and "Karnataka" in c["details"] and "2015" in c["details"]


def test_cin_bad_format():
    assert cin_check("CIN U7290KA2015PTC12345 Acme Pvt Ltd")[0]["status"] in ("warning", "not_checked")
    assert live.decode_cin("U7290KA2015PTC12345") is None


def test_cin_private_listed_contradiction():
    c = cin_check("Acme Pvt Ltd, CIN L72900KA2015PTC123456")[0]
    assert c["status"] == "warning" and "listed" in c["details"]


def test_cin_since_older_than_incorporation():
    c = cin_check("Acme Pvt Ltd, operating since 1995, CIN U72900KA2015PTC123456")[0]
    assert c["status"] == "warning" and "1995" in c["details"]


def test_cin_future_year():
    assert cin_check("Acme Pvt Ltd CIN U72900KA2099PTC123456")[0]["status"] == "warning"


def test_patterns_lookalike_and_tld():
    t = "Offer from Northwind Tech Pvt Ltd. Apply at https://northwind-careers.xyz/apply or bit.ly/abc. HR: hr@northwind-jobs.com"
    c = live.check_patterns(extract_fields(t), t)
    assert c["status"] == "warning" and "imitates" in c["details"]


def test_patterns_clean():
    t = "Offer from Northwind Tech Pvt Ltd. Reply to hr@northwindtech.com"
    assert live.check_patterns(extract_fields(t), t)["status"] == "no_match"


def test_patterns_personal_email_ignored():
    t = "Hiring now. Mail hr@gmail.com"
    assert live.check_patterns(extract_fields(t), t)["status"] == "not_checked"


def test_registrable():
    assert live.registrable("careers.acme.co.in") == "acme.co.in"
    assert live.registrable("a.b.example.com") == "example.com"


def test_live_disabled_is_not_checked():
    out = asyncio.run(live.check_live(extract_fields("Mail hr@acme-jobs.com"), "x"))
    assert all(c["status"] == "not_checked" for c in out)


def test_young_domain_rule_severity():
    base = {"name": "domain_age", "status": "warning", "source": "s", "checked_at": "t", "details": "x.com: registered 3 days ago"}
    f = run_rules("hello", extract_fields("hello"), [dict(base, min_age_days=3)])
    assert any(x["rule_id"] == "RULE-15" and x["severity"] == "strong" for x in f)
    f = run_rules("hello", extract_fields("hello"), [dict(base, min_age_days=100)])
    assert any(x["rule_id"] == "RULE-15" and x["severity"] == "medium" for x in f)


def test_live_with_fake_network(monkeypatch):
    monkeypatch.setenv("OFFERGUARD_LIVE", "1")
    new = datetime.now(timezone.utc) - timedelta(days=5)

    async def fake_rdap(c, d): return new, None
    async def fake_doh(c, n, t): return {"status": 3, "answers": []}
    async def fake_trace(c, u, max_hops=4): return [("bit.ly", 301), ("evil-site.top", 200)], "ok"
    monkeypatch.setattr(live, "rdap_created", fake_rdap)
    monkeypatch.setattr(live, "doh", fake_doh)
    monkeypatch.setattr(live, "trace_redirects", fake_trace)
    t = "Apply at https://acme-careers.top/x . Mail hr@acme-careers.top"
    out = {c["name"]: c for c in asyncio.run(live.check_live(extract_fields(t), t))}
    assert out["domain_age"]["status"] == "warning" and out["domain_age"]["min_age_days"] == 5
    assert out["dns_mail_records"]["status"] == "warning"
    assert out["link_redirects"]["status"] == "warning"


def test_live_failure_is_unavailable(monkeypatch):
    monkeypatch.setenv("OFFERGUARD_LIVE", "1")
    async def boom(c, d): return None, "error"
    async def none(c, n, t): return None
    async def tr(c, u, max_hops=4): return [], "error"
    monkeypatch.setattr(live, "rdap_created", boom); monkeypatch.setattr(live, "doh", none); monkeypatch.setattr(live, "trace_redirects", tr)
    t = "Apply at https://acme-careers.com/x"
    out = {c["name"]: c for c in asyncio.run(live.check_live(extract_fields(t), t))}
    assert all(out[n]["status"] == "unavailable" for n in out)
