"""
/**
 * @file test_main.py
 * @brief Unit tests for the main FastAPI application endpoints
 * @author Huy Le (huyisme-005)
 */
"""

from fastapi.testclient import TestClient
import logging
import json
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../app'))
from app.api_doc_scraper import (
    scrape_openapi, 
    scrape_html_doc, 
    debug_schema_extraction, 
    validate_schema_extraction
)
from app.main import app
from app.utils.dynamodb_snapshots import store_schema_snapshot, get_schema_by_version

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

    logging.info("Running test_health")
    r = client.get("/health")
    logging.info("Response: %s", json.dumps(r.json(), indent=2))
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

    logging.info("Running test_parse_missing_fields")
    r = client.post("/parse-request", json={"user_input": ""})
    logging.info("Response: %s", json.dumps(r.json(), indent=2))
    assert r.status_code == 422

def test_parse_valid_input():
    """
    /**
     * @brief Tests the parse-request endpoint with valid input
     * @return None
     * @throws AssertionError if the API doesn't process valid input correctly
     * @details Verifies that valid user input returns 200 status with trace_id and flow
     */
    """
    logging.info("Running test_parse_valid_input")
    r = client.post("/parse-request", json={"user_input": "Send welcome email"})
    logging.info("Response: %s", json.dumps(r.json(), indent=2))
    assert r.status_code == 200
    assert "trace_id" in r.json()
    assert "flow" in r.json()

def test_openapi_scraping():
    # Use a stable, public OpenAPI spec (Swagger Petstore)
    petstore_url = "https://petstore.swagger.io/v2/swagger.json"
    endpoints = scrape_openapi(petstore_url)
    assert isinstance(endpoints, list)
    assert len(endpoints) > 0
    validation = validate_schema_extraction(endpoints)
    assert validation["status"] == "success"

def test_html_scraping():
    test_url = "https://httpbin.org/json"
    endpoints = scrape_html_doc(test_url)
    assert isinstance(endpoints, list)
    validation = validate_schema_extraction(endpoints)
    assert "status" in validation

def test_debug_function():
    test_url = "https://petstore.swagger.io/v2/swagger.json"
    # This just checks that the debug function runs without error
    try:
        debug_schema_extraction(test_url)
    except Exception as e:
        assert False, f"debug_schema_extraction raised an exception: {e}"

def test_schema_validation():
    sample_endpoints = [
        {
            'method': 'GET',
            'path': '/users',
            'auth_type': 'bearer_token',
            'input_schema': {'type': 'none'},
            'output_schema': {'type': 'json', 'status_code': '200'}
        },
        {
            'method': 'POST',
            'path': '/users',
            'auth_type': 'none',
            'input_schema': {'type': 'unknown'},
            'output_schema': {'type': 'unknown'}
        },
        {
            'method': 'PUT',
            'path': '/users/{id}',
            'auth_type': 'api_key',
            'input_schema': {'type': 'json'},
            'output_schema': {'type': 'json', 'status_code': '200'}
        }
    ]
    validation = validate_schema_extraction(sample_endpoints)
    assert validation["total_endpoints"] == 3
    assert "auth_detection_rate" in validation
    assert "input_schema_rate" in validation
    assert "output_schema_rate" in validation

def test_dynamodb_store_and_retrieve():
    api_name = "TestAPI"
    endpoint = "/test/endpoint"
    method = "GET"
    schema = {"input": {"foo": "bar"}, "output": {"baz": "qux"}}
    metadata = {"auth_type": "None", "source_url": "http://example.com", "version_ts": "2025-01-01T00:00:00Z"}
    ts = int(time.time())
    # Store
    item = store_schema_snapshot(api_name, endpoint, method, schema, metadata, timestamp=ts)
    assert item["api_name"] == api_name
    # Retrieve
    retrieved = get_schema_by_version(api_name, ts)
    assert retrieved is not None
    assert retrieved["api_name"] == api_name
    assert retrieved["endpoint"] == endpoint
    assert retrieved["method"] == method
    assert retrieved["schema"] == schema
    assert retrieved["metadata"] == metadata

def test_schema_snapshot_endpoint():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    api_name = "TestAPI"
    endpoint = "/test/endpoint"
    method = "POST"
    schema = {"input": {"foo": "bar"}, "output": {"baz": "qux"}}
    metadata = {"auth_type": "OAuth", "source_url": "http://example.com", "version_ts": "2025-01-01T00:00:00Z"}
    ts = int(time.time())
    store_schema_snapshot(api_name, endpoint, method, schema, metadata, timestamp=ts)
    r = client.get(f"/schema-snapshot?api_name={api_name}&timestamp={ts}")
    assert r.status_code == 200
    data = r.json()
    assert data["api_name"] == api_name
    assert data["endpoint"] == endpoint
    assert data["method"] == method
    assert data["schema_json"] == schema
    assert data["auth_type"] == metadata["auth_type"]
    assert data["source_url"] == metadata["source_url"]
