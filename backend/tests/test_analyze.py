import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from fastapi.testclient import TestClient
from main import app
c = TestClient(app)

def test_health(): assert c.get("/health").json() == {"status": "healthy"}
def test_empty(): assert c.post("/analyze", json={"text": "  "}).status_code == 422
def test_too_long(): assert c.post("/analyze", json={"text": "a" * 20001}).status_code == 413
def test_ok():
    r = c.post("/analyze", json={"text": "Pay registration fee Rs 500"}).json()
    assert set(r) >= {"extracted_fields", "findings", "checks", "assessment", "missing_checks", "limitations"}
def test_bad_pdf(): assert c.post("/analyze-pdf", files={"file": ("a.pdf", b"nope", "application/pdf")}).status_code == 422
def test_history_disabled(): assert c.get("/history").json()["enabled"] is False
