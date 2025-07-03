"""
Tests for the dashboard API endpoints
"""

import pytest
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../app'))
from app.main import app

client = TestClient(app)

@pytest.mark.dashboard
def test_get_scan_history():
    """Test getting scan history"""
    with patch('app.dashboard_api.metadata_table.scan') as mock_scan:
        mock_scan.return_value = {
            'Items': [
                {
                    'scan_id': 'test_scan_1',
                    'timestamp': int(time.time()),
                    'results': [
                        {
                            'api_name': 'TestAPI',
                            'timestamp': int(time.time()),
                            'endpoints_count': 10,
                            'status': 'success'
                        }
                    ],
                    'total_apis_scanned': 1,
                    'successful_scans': 1
                }
            ]
        }
        response = client.get("/dashboard/scan-history?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:  # If there are scans
            assert "scan_id" in data[0]
            assert "timestamp" in data[0]
            assert "results" in data[0]

@pytest.mark.dashboard
def test_get_api_summary():
    """Test getting API summary"""
    try:
        response = client.get("/dashboard/api-summary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:  # If there are APIs
            assert "api_name" in data[0]
            assert "last_scan_timestamp" in data[0]
            assert "total_endpoints" in data[0]
            assert "recent_changes" in data[0]
    except Exception as e:
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            pytest.skip("AWS credentials not configured for dashboard testing")
        elif "ResourceNotFoundException" in str(e):
            pytest.skip("DynamoDB table not found - expected in test environment")
        else:
            raise e

@pytest.mark.dashboard
def test_rescan_api():
    """Test manual API rescan"""
    with patch('app.dashboard_api.schema_table.put_item') as mock_put, \
         patch('app.dashboard_api.schema_table.query') as mock_query, \
         patch('app.api_doc_scraper.scrape_openapi') as mock_scrape:
        mock_scrape.return_value = [
            {
                'method': 'GET',
                'path': '/test',
                'auth_type': 'none',
                'input_schema': {'type': 'none'},
                'output_schema': {'type': 'json'}
            }
        ]
        mock_query.return_value = {'Items': []}  # No previous scans
        rescan_data = {
            "api_name": f"TestAPI_Rescan_{int(time.time())}",
            "openapi_url": "https://petstore.swagger.io/v2/swagger.json"
        }
        response = client.post("/dashboard/rescan-api", json=rescan_data)
        assert response.status_code == 200
        data = response.json()
        assert "api_name" in data
        assert "timestamp" in data
        assert "endpoints_count" in data
        assert "changes_detected" in data
        assert "changes_summary" in data

@pytest.mark.dashboard
def test_get_api_changes():
    """Test getting API changes for a specific API"""
    try:
        # Use a unique API name that won't conflict
        unique_api_name = f"TestAPI_Changes_{int(time.time())}"
        response = client.get(f"/dashboard/api-changes/{unique_api_name}")
        assert response.status_code == 200
        data = response.json()
        assert "api_name" in data
        assert "scans" in data
        assert "total_scans" in data
    except Exception as e:
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            pytest.skip("AWS credentials not configured for dashboard testing")
        elif "ResourceNotFoundException" in str(e):
            pytest.skip("DynamoDB table not found - expected in test environment")
        else:
            raise e

@pytest.mark.dashboard
def test_rescan_api_invalid_url():
    """Test rescan with invalid URL"""
    with patch('app.api_doc_scraper.scrape_openapi', return_value=[]), \
         patch('app.dashboard_api.schema_table.put_item'), \
         patch('app.dashboard_api.schema_table.query', return_value={'Items': []}):
        rescan_data = {
            "api_name": "TestAPI_Invalid",
            "openapi_url": "http://invalid-url-that-does-not-exist.com"
        }
        response = client.post("/dashboard/rescan-api", json=rescan_data)
        # Should return 400 for invalid URL
        assert response.status_code == 400

@pytest.mark.dashboard
def test_rescan_api_missing_fields():
    """Test rescan with missing required fields"""
    try:
        # Missing openapi_url
        rescan_data = {
            "api_name": "TestAPI_Missing"
        }
        response = client.post("/dashboard/rescan-api", json=rescan_data)
        assert response.status_code == 422  # Validation error
    except Exception as e:
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            pytest.skip("AWS credentials not configured for dashboard testing")
        elif "ResourceNotFoundException" in str(e):
            pytest.skip("DynamoDB table not found - expected in test environment")
        else:
            raise e

@pytest.mark.dashboard
def test_scan_history_pagination():
    """Test scan history with different limit values"""
    with patch('app.dashboard_api.metadata_table.scan') as mock_scan:
        mock_scan.return_value = {
            'Items': [
                {
                    'scan_id': 'test_scan_1',
                    'timestamp': int(time.time()),
                    'results': [
                        {
                            'api_name': 'TestAPI',
                            'timestamp': int(time.time()),
                            'endpoints_count': 10,
                            'status': 'success'
                        }
                    ],
                    'total_apis_scanned': 1,
                    'successful_scans': 1
                }
            ]
        }
        # Test with limit=1
        response = client.get("/dashboard/scan-history?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
        # Test with limit=10
        response = client.get("/dashboard/scan-history?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10

@pytest.mark.dashboard
def test_api_changes_pagination():
    """Test API changes with different limit values"""
    try:
        unique_api_name = f"TestAPI_Pagination_{int(time.time())}"
        response = client.get(f"/dashboard/api-changes/{unique_api_name}?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "scans" in data
        assert len(data["scans"]) <= 5
    except Exception as e:
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            pytest.skip("AWS credentials not configured for dashboard testing")
        elif "ResourceNotFoundException" in str(e):
            pytest.skip("DynamoDB table not found - expected in test environment")
        else:
            raise e

@pytest.mark.dashboard
def test_dashboard_endpoints_with_mock():
    """Test dashboard endpoints with mocked AWS services"""
    with patch('app.dashboard_api.metadata_table.scan') as mock_scan:
        mock_scan.return_value = {
            'Items': [
                {
                    'scan_id': 'test_scan_1',
                    'timestamp': int(time.time()),
                    'results': [
                        {
                            'api_name': 'TestAPI',
                            'timestamp': int(time.time()),
                            'endpoints_count': 10,
                            'status': 'success'
                        }
                    ],
                    'total_apis_scanned': 1,
                    'successful_scans': 1
                }
            ]
        }
        
        response = client.get("/dashboard/scan-history?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['scan_id'] == 'test_scan_1'

@pytest.mark.dashboard
def test_api_summary_with_mock():
    """Test API summary with mocked AWS services"""
    with patch('app.dashboard_api.schema_table.scan') as mock_scan, \
         patch('app.dashboard_api.schema_table.query') as mock_query:
        
        mock_scan.return_value = {
            'Items': [
                {'api_name': 'TestAPI1'},
                {'api_name': 'TestAPI2'}
            ]
        }
        
        mock_query.return_value = {
            'Items': [
                {
                    'api_name': 'TestAPI1',
                    'timestamp': str(int(time.time())),
                    'endpoint': '/test',
                    'method': 'GET',
                    'schema': {'input': {}, 'output': {}},
                    'metadata': {'auth_type': 'none', 'source_url': 'http://test.com'}
                }
            ]
        }
        
        response = client.get("/dashboard/api-summary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.dashboard
def test_error_handling():
    """Test error handling in dashboard endpoints"""
    with patch('app.dashboard_api.metadata_table.scan', side_effect=Exception("AWS Error")):
        response = client.get("/dashboard/scan-history")
        assert response.status_code == 500
        data = response.json()
        assert "Error retrieving scan history" in data['detail']

@pytest.mark.dashboard
def test_aws_credentials_error():
    """Test handling of AWS credentials errors"""
    with patch('app.dashboard_api.metadata_table.scan', side_effect=Exception("NoCredentialsError")):
        response = client.get("/dashboard/scan-history")
        assert response.status_code == 503
        data = response.json()
        assert "AWS credentials not configured" in data['detail']

@pytest.mark.dashboard
def test_dynamodb_table_not_found():
    """Test handling of DynamoDB table not found errors"""
    with patch('app.dashboard_api.metadata_table.scan', side_effect=Exception("ResourceNotFoundException")):
        response = client.get("/dashboard/scan-history")
        assert response.status_code == 404
        data = response.json()
        assert "Scan metadata table not found" in data['detail'] 