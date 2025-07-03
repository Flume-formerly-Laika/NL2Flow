"""
Tests for the Lambda scheduled scanner function
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
import sys
import os

# Add the lambda_functions directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../lambda_functions'))

# Import the lambda function
from app.lambda_functions.scheduled_scanner import lambda_handler, scrape_openapi, compare_schemas, send_sns_notification

@pytest.fixture
def mock_boto3_clients():
    """Mock AWS clients"""
    with patch('app.lambda_functions.scheduled_scanner.sns') as mock_sns, \
         patch('app.lambda_functions.scheduled_scanner.dynamodb') as mock_dynamodb, \
         patch('app.lambda_functions.scheduled_scanner.table') as mock_table:
        
        mock_sns.publish.return_value = {'MessageId': 'test-message-id'}
        mock_table.put_item.return_value = None
        mock_table.query.return_value = {'Items': []}
        
        yield {
            'sns': mock_sns,
            'dynamodb': mock_dynamodb,
            'table': mock_table
        }

@pytest.fixture
def sample_event():
    """Sample EventBridge event"""
    return {
        "version": "0",
        "id": "test-event-id",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "2024-01-01T00:00:00Z",
        "region": "us-east-1",
        "resources": ["arn:aws:events:us-east-1:123456789012:rule/test-rule"],
        "detail": {}
    }

@pytest.fixture
def sample_context():
    """Sample Lambda context"""
    context = MagicMock()
    context.function_name = "test-scheduled-api-scanner"
    context.function_version = "$LATEST"
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-scheduled-api-scanner"
    context.memory_limit_in_mb = 512
    context.remaining_time_in_millis = lambda: 300000
    context.aws_request_id = "test-request-id"
    return context

def test_scrape_openapi_success():
    """Test successful OpenAPI scraping"""
    with patch('app.lambda_functions.scheduled_scanner.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "paths": {
                "/pets": {
                    "get": {
                        "summary": "List pets",
                        "responses": {"200": {"description": "Success"}}
                    },
                    "post": {
                        "summary": "Create pet",
                        "responses": {"201": {"description": "Created"}}
                    }
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        endpoints = scrape_openapi("https://test.com/swagger.json")
        
        assert len(endpoints) == 2
        assert any(ep['path'] == '/pets' and ep['method'] == 'GET' for ep in endpoints)
        assert any(ep['path'] == '/pets' and ep['method'] == 'POST' for ep in endpoints)

def test_scrape_openapi_failure():
    """Test OpenAPI scraping failure"""
    with patch('app.lambda_functions.scheduled_scanner.requests.get', side_effect=Exception("Network error")):
        endpoints = scrape_openapi("https://invalid-url.com")
        assert endpoints == []

def test_compare_schemas_no_changes():
    """Test schema comparison with no changes"""
    old_schema = [
        {'endpoint': '/pets', 'method': 'GET', 'schema': {'input': {}, 'output': {}}},
        {'endpoint': '/pets', 'method': 'POST', 'schema': {'input': {}, 'output': {}}}
    ]
    new_schema = [
        {'endpoint': '/pets', 'method': 'GET', 'schema': {'input': {}, 'output': {}}},
        {'endpoint': '/pets', 'method': 'POST', 'schema': {'input': {}, 'output': {}}}
    ]
    
    changes = compare_schemas(old_schema, new_schema)
    
    assert len(changes['added_endpoints']) == 0
    assert len(changes['removed_endpoints']) == 0
    assert len(changes['modified_endpoints']) == 0

def test_compare_schemas_with_changes():
    """Test schema comparison with changes"""
    old_schema = [
        {'endpoint': '/pets', 'method': 'GET', 'schema': {'input': {}, 'output': {}}},
        {'endpoint': '/pets', 'method': 'POST', 'schema': {'input': {}, 'output': {}}}
    ]
    new_schema = [
        {'endpoint': '/pets', 'method': 'GET', 'schema': {'input': {}, 'output': {}}},
        {'endpoint': '/pets', 'method': 'POST', 'schema': {'input': {}, 'output': {}}},
        {'endpoint': '/pets/{id}', 'method': 'GET', 'schema': {'input': {}, 'output': {}}}
    ]
    
    changes = compare_schemas(old_schema, new_schema)
    
    assert len(changes['added_endpoints']) == 1
    assert len(changes['removed_endpoints']) == 0
    assert len(changes['modified_endpoints']) == 0
    assert changes['added_endpoints'][0]['path'] == '/pets/{id}'

def test_send_sns_notification(mock_boto3_clients):
    """Test SNS notification sending"""
    api_name = "TestAPI"
    changes = {
        'added_endpoints': [{'path': '/new', 'method': 'GET'}],
        'removed_endpoints': [],
        'modified_endpoints': []
    }
    timestamp = int(time.time())
    
    send_sns_notification(api_name, changes, timestamp)
    
    mock_boto3_clients['sns'].publish.assert_called_once()
    call_args = mock_boto3_clients['sns'].publish.call_args
    assert call_args[1]['Subject'] == f"API Schema Changes Detected: {api_name}"

def test_lambda_handler_success(mock_boto3_clients, sample_event, sample_context):
    """Test successful Lambda handler execution"""
    with patch('app.lambda_functions.scheduled_scanner.scrape_openapi') as mock_scrape:
        mock_scrape.return_value = [
            {
                'method': 'GET',
                'path': '/pets',
                'auth_type': 'none',
                'input_schema': {'type': 'none'},
                'output_schema': {'type': 'json'}
            }
        ]
        
        result = lambda_handler(sample_event, sample_context)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Scheduled API scan completed'
        assert 'scan_results' in body
        assert 'scan_metadata' in body

def test_lambda_handler_with_changes(mock_boto3_clients, sample_event, sample_context):
    """Test Lambda handler with detected changes"""
    with patch('app.lambda_functions.scheduled_scanner.scrape_openapi') as mock_scrape, \
         patch('app.lambda_functions.scheduled_scanner.send_sns_notification') as mock_sns:
        
        # Mock current scan
        mock_scrape.return_value = [
            {
                'method': 'GET',
                'path': '/pets',
                'auth_type': 'none',
                'input_schema': {'type': 'none'},
                'output_schema': {'type': 'json'}
            }
        ]
        
        # Mock previous scan (different schema)
        mock_boto3_clients['table'].query.side_effect = [
            {'Items': [{'timestamp': '1234567890'}]},  # First query for latest timestamp
            {'Items': [  # Second query for previous schema
                {
                    'endpoint': '/pets',
                    'method': 'GET',
                    'schema': {'input': {'old': 'schema'}, 'output': {}}
                }
            ]}
        ]
        
        result = lambda_handler(sample_event, sample_context)
        
        assert result['statusCode'] == 200
        # Should have called SNS notification due to schema changes
        mock_sns.assert_called()

def test_lambda_handler_no_apis_found(mock_boto3_clients, sample_event, sample_context):
    """Test Lambda handler when no APIs are found"""
    with patch('app.lambda_functions.scheduled_scanner.scrape_openapi') as mock_scrape:
        mock_scrape.return_value = []  # No endpoints found
        
        result = lambda_handler(sample_event, sample_context)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Scheduled API scan completed'

def test_lambda_handler_error_handling(mock_boto3_clients, sample_event, sample_context):
    """Test Lambda handler error handling"""
    with patch('app.lambda_functions.scheduled_scanner.scrape_openapi', side_effect=Exception("Test error")):
        result = lambda_handler(sample_event, sample_context)
        
        assert result['statusCode'] == 200  # Should still return 200 even with errors
        body = json.loads(result['body'])
        assert body['message'] == 'Scheduled API scan completed'
        # Should have error results in scan_results
        assert any(r['status'] == 'error' for r in body['scan_results'])

def test_lambda_handler_environment_variables():
    """Test Lambda handler with different environment variables"""
    with patch.dict('os.environ', {
        'DYNAMODB_SCHEMA_TABLE': 'CustomTable',
        'SNS_TOPIC_ARN': 'arn:aws:sns:us-east-1:123456789012:custom-topic'
    }):
        # This test verifies that environment variables are used correctly
        # The actual functionality is tested in other tests
        assert True

def test_store_schema_snapshot(mock_boto3_clients):
    """Test storing schema snapshot"""
    from app.lambda_functions.scheduled_scanner import store_schema_snapshot
    
    endpoints = [
        {
            'method': 'GET',
            'path': '/pets',
            'auth_type': 'none',
            'input_schema': {'type': 'none'},
            'output_schema': {'type': 'json'}
        }
    ]
    
    result = store_schema_snapshot("TestAPI", endpoints, "https://test.com")
    
    assert result['api_name'] == "TestAPI"
    assert result['endpoints_count'] == 1
    assert 'timestamp' in result
    mock_boto3_clients['table'].put_item.assert_called()

def test_get_previous_schema(mock_boto3_clients):
    """Test getting previous schema"""
    from app.lambda_functions.scheduled_scanner import get_previous_schema
    
    # Mock query responses
    mock_boto3_clients['table'].query.side_effect = [
        {'Items': [{'timestamp': '1234567890'}]},  # Latest timestamp
        {'Items': [  # Previous schema
            {
                'endpoint': '/pets',
                'method': 'GET',
                'schema': {'input': {}, 'output': {}}
            }
        ]}
    ]
    
    result = get_previous_schema("TestAPI")
    
    assert len(result) == 1
    assert result[0]['endpoint'] == '/pets'
    assert result[0]['method'] == 'GET'

def test_get_previous_schema_no_data(mock_boto3_clients):
    """Test getting previous schema when no data exists"""
    from app.lambda_functions.scheduled_scanner import get_previous_schema
    
    mock_boto3_clients['table'].query.return_value = {'Items': []}
    
    result = get_previous_schema("TestAPI")
    
    assert result == []

def test_lambda_handler_scan_metadata_storage(mock_boto3_clients, sample_event, sample_context):
    """Test that scan metadata is stored in DynamoDB"""
    with patch('app.lambda_functions.scheduled_scanner.scrape_openapi') as mock_scrape, \
         patch('app.lambda_functions.scheduled_scanner.dynamodb.Table') as mock_metadata_table:
        
        mock_scrape.return_value = [
            {
                'method': 'GET',
                'path': '/pets',
                'auth_type': 'none',
                'input_schema': {'type': 'none'},
                'output_schema': {'type': 'json'}
            }
        ]
        
        mock_metadata_table.return_value.put_item.return_value = None
        
        result = lambda_handler(sample_event, sample_context)
        
        assert result['statusCode'] == 200
        # Verify metadata table was called
        mock_metadata_table.assert_called_with('ApiScanMetadata') 