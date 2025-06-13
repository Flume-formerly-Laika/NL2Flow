from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}

def test_parse_missing_fields():
    r = client.post("/parse-request", json={"user_input": ""})
    assert r.status_code == 422
