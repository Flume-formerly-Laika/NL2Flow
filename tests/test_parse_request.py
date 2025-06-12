'''
@file test_parse_request.py
@author Huy Le (huyisme-005)
@brief test user signup
'''

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_parse_request_success():
    response = client.post("/parse-request", json={"user_input": "When a user signs up, send a welcome email"})
    assert response.status_code == 200
    assert "flow" in response.json()
    assert "trace_id" in response.json()

def test_parse_request_failure():
    response = client.post("/parse-request", json={"user_input": ""})
    assert response.status_code == 400
