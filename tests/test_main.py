"""
/**
 * @file test_main.py
 * @brief Unit tests for the main FastAPI application endpoints
 * @author Huy Le (huyisme-005)
 */
"""

from fastapi.testclient import TestClient

from app.main import app



client = TestClient(app)

"""
/**
 * @var client
 * @brief Test client for making HTTP requests to the FastAPI application
 * @type TestClient
 */
"""

def test_health():

    """
    /**
     * @brief Tests the health endpoint for proper response
     * @return None
     * @throws AssertionError if the health check fails
     * @details Verifies that /health returns 200 status and correct JSON response
     */
    """

    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok", "message": "NL2Flow API is running"}

def test_parse_missing_fields():

    """
    /**
     * @brief Tests the parse-request endpoint with invalid input
     * @return None
     * @throws AssertionError if validation doesn't work as expected
     * @details Verifies that empty user_input triggers proper validation error (422)
     */
    """

    r = client.post("/parse-request", json={"user_input": ""})
    
    assert r.status_code == 422
