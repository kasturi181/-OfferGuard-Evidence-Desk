import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from fastapi.testclient import TestClient
from main import app
c = TestClient(app)

def test_health(): assert c.get("/health").json()["status"] == "healthy"
def test_empty(): assert c.post("/analyze", json={"text": "  "}).status_code == 422
def test_too_long(): assert c.post("/analyze", json={"text": "a" * 20001}).status_code == 413
def test_ok():
    r = c.post("/analyze", json={"text": "Pay registration fee Rs 500"}).json()
    assert set(r) >= {"extracted_fields", "findings", "checks", "assessment", "missing_checks", "limitations"}
def test_bad_pdf(): assert c.post("/analyze-pdf", files={"file": ("a.pdf", b"nope", "application/pdf")}).status_code == 422
def test_history_disabled(): assert c.get("/history").json()["enabled"] is False


def test_report_disabled():
    assert c.post("/report", json={"kind": "email", "value": "x@y.com", "description": "t"}).status_code == 503

def test_report_validation():
    assert c.post("/report", json={"kind": "bad", "value": "abc"}).status_code == 422

def test_stats_disabled():
    j = c.get("/stats").json()
    assert j["enabled"] is False and j["companies_in_dataset"] >= 3

def test_root():
    assert c.get("/").json()["service"] == "OfferGuard API"
