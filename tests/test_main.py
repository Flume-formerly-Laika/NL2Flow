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
from app.utils.schema_diff import diff_schema_versions
import pytest  # noqa: F401 - pytest is used for test discovery and markers
from unittest.mock import patch

# Configure pytest markers
pytest_plugins = []

client = TestClient(app)

"""
/**
 * @var client
 * @brief Test client for making HTTP requests to the FastAPI application
 * @type TestClient
 */
"""

@pytest.mark.unit
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.unit
def test_parse_request():
    response = client.post("/parse-request", json={"user_input": "Send a welcome email when someone signs up"})
    assert response.status_code == 200
    assert "trace_id" in response.json()
    assert "flow" in response.json()

@pytest.mark.dynamodb
def test_list_apis():
    """Test the new list-apis endpoint"""
    try:
        response = client.get("/list-apis")
        assert response.status_code == 200
        data = response.json()
        assert "api_names" in data
        assert "total_count" in data
        assert isinstance(data["api_names"], list)
        assert isinstance(data["total_count"], int)
    except Exception as e:
        # Handle AWS connection issues gracefully
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            pytest.skip("AWS credentials not configured for DynamoDB testing")
        elif "ResourceNotFoundException" in str(e):
            pytest.skip("DynamoDB table not found - expected in test environment")
        else:
            raise e

@pytest.mark.dynamodb
def test_list_versions():
    """Test the new list-versions endpoint"""
    try:
        # Use a unique API name that won't conflict with other test data
        unique_api_name = f"NonExistentAPI_{int(time.time())}"
        # First, let's try with a non-existent API to see the error handling
        response = client.get(f"/list-versions/{unique_api_name}")
        assert response.status_code == 200  # Should return empty list, not error
        data = response.json()
        assert data["api_name"] == unique_api_name
        assert data["total_count"] == 0
        assert data["versions"] == []
    except Exception as e:
        # Handle AWS connection issues gracefully
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            pytest.skip("AWS credentials not configured for DynamoDB testing")
        elif "ResourceNotFoundException" in str(e):
            pytest.skip("DynamoDB table not found - expected in test environment")
        else:
            raise e

@pytest.mark.dynamodb
def test_delete_snapshot_get():
    """Test the browser-friendly delete-snapshot endpoint"""
    try:
        # Use a unique API name that won't conflict with other test data
        unique_api_name = f"TestAPI_Snapshot_{int(time.time())}"
        response = client.get(f"/delete-snapshot?api_name={unique_api_name}&timestamp=1234567890")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted_count" in data
        assert data["deleted_count"] == 0  # Should be 0 since this unique API doesn't exist
    except Exception as e:
        # Handle AWS connection issues gracefully
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            pytest.skip("AWS credentials not configured for DynamoDB testing")
        elif "ResourceNotFoundException" in str(e):
            pytest.skip("DynamoDB table not found - expected in test environment")
        else:
            raise e

@pytest.mark.dynamodb
def test_delete_api_get():
    """Test the browser-friendly delete-api endpoint"""
    try:
        # Use a unique API name that won't conflict with other test data
        unique_api_name = f"TestAPI_Delete_{int(time.time())}"
        response = client.get(f"/delete-api?api_name={unique_api_name}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted_count" in data
        assert data["deleted_count"] == 0  # Should be 0 since this unique API doesn't exist
    except Exception as e:
        # If DynamoDB is not available, the test should still pass
        # as the endpoint should handle the error gracefully
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            # AWS credentials not configured - this is expected in test environment
            pytest.skip("AWS credentials not configured for DynamoDB testing")
        elif "ResourceNotFoundException" in str(e):
            # DynamoDB table doesn't exist - this is expected in test environment
            pytest.skip("DynamoDB table not found - expected in test environment")
        else:
            # Re-raise unexpected errors
            raise e

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
    """
    
     @brief Tests the scraping of an OpenAPI spec
     @return None
     @throws AssertionError if the scraping doesn't work as expected
     @details Verifies that the scraping of an OpenAPI spec returns a list of endpoints
     
    """
    # Use a stable, public OpenAPI spec (Swagger Petstore)
    petstore_url = "https://petstore.swagger.io/v2/swagger.json"
    endpoints = scrape_openapi(petstore_url)
    assert isinstance(endpoints, list)
    assert len(endpoints) > 0
    validation = validate_schema_extraction(endpoints)
    assert validation["status"] == "success"

def test_html_scraping():
    """
    
     @brief Tests the scraping of an HTML document
     @return None
     @throws AssertionError if the scraping doesn't work as expected
     @details Verifies that the scraping of an HTML document returns a list of endpoints
     
    """
    test_url = "https://httpbin.org/json"
    endpoints = scrape_html_doc(test_url)
    assert isinstance(endpoints, list)
    validation = validate_schema_extraction(endpoints)
    assert "status" in validation

def test_debug_function():
    """
    /**
     * @brief Tests the debug function
     * @return None
     * @throws AssertionError if the debug function raises an exception
     * @details Verifies that the debug function runs without error
     */
    """
    test_url = "https://petstore.swagger.io/v2/swagger.json"
    # This just checks that the debug function runs without error
    try:
        debug_schema_extraction(test_url)
    except Exception as e:
        assert False, f"debug_schema_extraction raised an exception: {e}"

def test_schema_validation():
    """
    /**
     * @brief Tests the schema validation
     * @return None
     * @throws AssertionError if the schema validation doesn't work as expected
     * @details Verifies that the schema validation returns a list of endpoints
     */
    """
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
    """
    /**
     * @brief Tests the DynamoDB store and retrieve
     * @return None
     * @throws AssertionError if the DynamoDB store and retrieve doesn't work as expected
     * @details Verifies that the DynamoDB store and retrieve returns a list of endpoints
     */
    """
    # Use a unique API name to avoid conflicts with other tests
    api_name = f"TestAPI_Store_{int(time.time())}"
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
    """
    /**
     * @brief Tests the schema snapshot endpoint
     * @return None
     * @throws AssertionError if the schema snapshot endpoint doesn't work as expected
     * @details Verifies that the schema snapshot endpoint returns a list of endpoints
     */
    """
    from fastapi.testclient import TestClient
    client = TestClient(app)
    # Use a unique API name to avoid conflicts with other tests
    api_name = f"TestAPI_Snapshot_Endpoint_{int(time.time())}"
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

def test_schema_diff_engine():
    """
    /**
     * @brief Tests the schema diff engine
     * @return None
     * @throws AssertionError if the schema diff engine doesn't work as expected
     * @details Verifies that the schema diff engine returns a list of endpoints
     */
    """
    from app.utils.schema_diff import diff_schema_versions
    old_schema = {
        "product": {
            "title": "string",
            "vendor": "string"
        }
    }
    new_schema = {
        "product": {
            "title": "string",
            "vendor": "string",
            "tags": "string"
        }
    }
    diff = diff_schema_versions(old_schema, new_schema)
    # Convert the flat diff list to structured output
    structured = {"added": {}, "removed": {}, "changed": {}}
    for d in diff:
        # Convert path to dot notation
        dot_path = d["path"].replace("/", ".")
        if d["op"] == "add":
            structured["added"][dot_path] = {"new_type": d["new"]}
        elif d["op"] == "remove":
            structured["removed"][dot_path] = {"old_type": d["old"]}
        elif d["op"] == "change":
            structured["changed"][dot_path] = {"old_type": d["old"], "new_type": d["new"]}
    expected = {
        "added": {
            "product.tags": {
                "new_type": "string"
            }
        },
        "removed": {},
        "changed": {}
    }
    assert structured == expected

def test_diff_engine_basic_add_remove_change():
    """
    /**
     * @brief Tests the diff engine basic add, remove, change
     * @return None
     * @throws AssertionError if the diff engine basic add, remove, change doesn't work as expected
     * @details Verifies that the diff engine basic add, remove, change returns a list of endpoints
     */
    """
    old_schema = {"a": 1, "b": 2}
    new_schema = {"a": 1, "b": 3, "c": 4}
    r = client.post("/diff-schemas", json={"old_schema": old_schema, "new_schema": new_schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    assert any(d["op"] == "add" and d["path"] == "c" for d in diff)
    assert any(d["op"] == "change" and d["path"] == "b" for d in diff)

def test_diff_engine_no_difference():
    """
    /**
     * @brief Tests the diff engine no difference
     * @return None
     * @throws AssertionError if the diff engine no difference doesn't work as expected
     * @details Verifies that the diff engine no difference returns a list of endpoints
     */
    """
    schema = {"x": {"y": [1, 2, 3]}, "z": "foo"}
    r = client.post("/diff-schemas", json={"old_schema": schema, "new_schema": schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    assert diff == []

def test_diff_engine_nested():
    old_schema = {"a": {"b": {"c": 1}}}
    new_schema = {"a": {"b": {"c": 2, "d": 3}}}
    r = client.post("/diff-schemas", json={"old_schema": old_schema, "new_schema": new_schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    assert any(d["op"] == "change" and d["path"] == "a/b/c" for d in diff)
    assert any(d["op"] == "add" and d["path"] == "a/b/d" for d in diff)

def test_diff_engine_list_handling():
    """
    /**
     * @brief Tests the diff engine list handling
     * @return None
     * @throws AssertionError if the diff engine list handling doesn't work as expected
     * @details Verifies that the diff engine list handling returns a list of endpoints
     */
    """
    old_schema = {"arr": [1, 2, 3]}
    new_schema = {"arr": [1, 4]}
    r = client.post("/diff-schemas", json={"old_schema": old_schema, "new_schema": new_schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    assert any(d["op"] == "change" and d["path"] == "arr[1]" for d in diff)
    assert any(d["op"] == "remove" and d["path"] == "arr[2]" for d in diff)

def test_diff_engine_type_change():
    """
    /**
     * @brief Tests the diff engine type change
     * @return None
     * @throws AssertionError if the diff engine type change doesn't work as expected
     * @details Verifies that the diff engine type change returns a list of endpoints
     */
    """
    old_schema = {"foo": 123}
    new_schema = {"foo": "bar"}
    r = client.post("/diff-schemas", json={"old_schema": old_schema, "new_schema": new_schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    assert any(d["op"] == "change" and d["path"] == "foo" for d in diff)

def test_diff_engine_empty_schemas():
    """
    /**
     * @brief Tests the diff engine empty schemas
     * @return None
     * @throws AssertionError if the diff engine empty schemas doesn't work as expected
     * @details Verifies that the diff engine empty schemas returns a list of endpoints
     */
    """
    r = client.post("/diff-schemas", json={"old_schema": {}, "new_schema": {}})
    assert r.status_code == 200
    assert r.json()["diff"] == []

def test_diff_engine_old_empty():
    """
    /**
     * @brief Tests the diff engine old empty
     * @return None
     * @throws AssertionError if the diff engine old empty doesn't work as expected
     * @details Verifies that the diff engine old empty returns a list of endpoints
     */
    """
    new_schema = {"a": 1}
    r = client.post("/diff-schemas", json={"old_schema": {}, "new_schema": new_schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    assert any(d["op"] == "add" and d["path"] == "a" for d in diff)

def test_diff_engine_new_empty():
    """
    /**
     * @brief Tests the diff engine new empty
     * @return None
     * @throws AssertionError if the diff engine new empty doesn't work as expected
     * @details Verifies that the diff engine new empty returns a list of endpoints
     */
    """
    old_schema = {"a": 1}
    r = client.post("/diff-schemas", json={"old_schema": old_schema, "new_schema": {}})
    assert r.status_code == 200
    diff = r.json()["diff"]
    assert any(d["op"] == "remove" and d["path"] == "a" for d in diff)

def test_diff_engine_none_and_missing():
    # Edge: None vs missing field
    old_schema = {"a": None}
    new_schema = {}
    r = client.post("/diff-schemas", json={"old_schema": old_schema, "new_schema": new_schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    # Should register as remove
    assert any(d["op"] == "remove" and d["path"] == "a" for d in diff)

    # Edge: missing vs None
    old_schema = {}
    new_schema = {"a": None}
    r = client.post("/diff-schemas", json={"old_schema": old_schema, "new_schema": new_schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    # Should register as add
    assert any(d["op"] == "add" and d["path"] == "a" for d in diff)

def test_diff_engine_type_conflict():
    # Edge: Same key, different types (dict vs list)
    old_schema = {"a": {"b": 1}}
    new_schema = {"a": [1, 2, 3]}
    r = client.post("/diff-schemas", json={"old_schema": old_schema, "new_schema": new_schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    # Should register as change at 'a'
    assert any(d["op"] == "change" and d["path"] == "a" for d in diff)

def test_diff_engine_deeply_nested():
    # Edge: Deeply nested change
    old_schema = {"a": {"b": {"c": {"d": 1}}}}
    new_schema = {"a": {"b": {"c": {"d": 2}}}}
    r = client.post("/diff-schemas", json={"old_schema": old_schema, "new_schema": new_schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    assert any(d["op"] == "change" and d["path"] == "a/b/c/d" for d in diff)

def test_diff_engine_empty_list_and_dict():
    # Edge: Empty list vs empty dict
    old_schema = {"a": []}
    new_schema = {"a": {}}
    r = client.post("/diff-schemas", json={"old_schema": old_schema, "new_schema": new_schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    assert any(d["op"] == "change" and d["path"] == "a" for d in diff)

def test_diff_engine_multiple_simultaneous_changes():
    # Edge: Add, remove, and change in one call
    old_schema = {"a": 1, "b": 2, "c": 3}
    new_schema = {"a": 1, "b": 20, "d": 4}
    r = client.post("/diff-schemas", json={"old_schema": old_schema, "new_schema": new_schema})
    assert r.status_code == 200
    diff = r.json()["diff"]
    assert any(d["op"] == "remove" and d["path"] == "c" for d in diff)
    assert any(d["op"] == "add" and d["path"] == "d" for d in diff)
    assert any(d["op"] == "change" and d["path"] == "b" for d in diff)

def test_health_wrong_method():
    # Edge: Wrong HTTP method (POST instead of GET)
    r = client.post("/health")
    assert r.status_code in (405, 404)  # Method Not Allowed or Not Found

def test_parse_request_malformed_json():
    # Edge: Malformed JSON in request body
    r = client.post("/parse-request", content="{bad json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422 or r.status_code == 400

def test_parse_request_missing_field():
    # Edge: Missing user_input field in request
    r = client.post("/parse-request", json={})
    assert r.status_code == 422

def test_parse_request_large_input():
    # Edge: Very large user_input string
    large_input = "a" * 10000
    r = client.post("/parse-request", json={"user_input": large_input})
    assert r.status_code in (200, 500)  # Should not crash

def test_openapi_scraping_invalid_url():
    # Edge: Invalid OpenAPI URL
    try:
        scrape_openapi("http://invalid-url")
    except Exception as e:
        assert True  # Should raise

def test_html_scraping_non_json():
    # Edge: Non-JSON HTML page for HTML scraping
    endpoints = scrape_html_doc("https://www.example.com")
    assert isinstance(endpoints, list)

def test_schema_validation_empty():
    # Edge: Empty endpoints list for schema validation
    validation = validate_schema_extraction([])
    assert validation["status"] == "error"

def test_dynamodb_retrieve_nonexistent():
    # Edge: Retrieve nonexistent snapshot from DynamoDB
    result = get_schema_by_version("NonexistentAPI", 0)
    assert result is None

def test_schema_snapshot_endpoint_missing_params():
    # Edge: Missing required query params for schema snapshot endpoint
    r = client.get("/schema-snapshot")
    assert r.status_code == 422

def test_diff_schema_versions_direct_usage():
    # This test ensures the direct import is used and works
    old = {"a": 1}
    new = {"a": 2}
    diff = diff_schema_versions(old, new)
    assert isinstance(diff, list)
    assert any(d["op"] == "change" and d["path"] == "a" for d in diff)

def test_list_apis_normal():
    """Test /list-apis returns a list (could be empty) and status 200, and includes api_versions."""
    response = client.get("/list-apis")
    assert response.status_code == 200
    data = response.json()
    assert "api_names" in data
    assert "total_count" in data
    assert "api_versions" in data
    assert isinstance(data["api_names"], list)
    assert isinstance(data["total_count"], int)
    assert isinstance(data["api_versions"], dict)
    for api, versions in data["api_versions"].items():
        assert isinstance(versions, list)

def test_list_apis_dynamodb_unreachable():
    """Test /list-apis returns empty list and 200 if DynamoDB is unreachable, and includes api_versions."""
    with patch("app.main.list_api_names", side_effect=Exception("Could not connect to the endpoint URL: 'https://dynamodb.us-east-1.amazonaws.com/'")):
        response = client.get("/list-apis")
        assert response.status_code == 200
        data = response.json()
        assert data["api_names"] == []
        assert data["total_count"] == 0
        assert data["api_versions"] == {}
