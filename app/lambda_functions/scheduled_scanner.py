"""
Lambda function for scheduled API scanning.
Triggered by EventBridge daily to scan APIs and detect changes.
"""

import json
import boto3
import os
import time
from datetime import datetime, timezone
import requests
from typing import Dict, List, Any

# Initialize AWS clients
sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_SCHEMA_TABLE', 'ApiSchemaSnapshots'))

# SNS Topic ARN for notifications
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:123456789012:api-schema-updated')

def scrape_openapi(openapi_url: str) -> List[Dict[str, Any]]:
    """Scrape OpenAPI specification and extract endpoints."""
    try:
        response = requests.get(openapi_url, timeout=30)
        response.raise_for_status()
        spec = response.json()
        
        endpoints = []
        if 'paths' in spec:
            for path, methods in spec['paths'].items():
                for method, details in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        endpoint = {
                            'method': method.upper(),
                            'path': path,
                            'auth_type': 'none',  # Default, can be enhanced
                            'input_schema': {'type': 'none'},
                            'output_schema': {'type': 'json', 'status_code': '200'}
                        }
                        endpoints.append(endpoint)
        
        return endpoints
    except Exception as e:
        print(f"Error scraping {openapi_url}: {e}")
        return []

def store_schema_snapshot(api_name: str, endpoints: List[Dict], source_url: str) -> Dict:
    """Store schema snapshot in DynamoDB."""
    timestamp = int(time.time())
    
    for endpoint in endpoints:
        item = {
            'api_name': api_name,
            'endpoint': endpoint['path'],
            'method': endpoint['method'],
            'timestamp': str(timestamp),
            'schema': {
                'input': endpoint['input_schema'],
                'output': endpoint['output_schema']
            },
            'metadata': {
                'auth_type': endpoint['auth_type'],
                'source_url': source_url,
                'version_ts': datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
            }
        }
        table.put_item(Item=item)
    
    return {
        'api_name': api_name,
        'timestamp': timestamp,
        'endpoints_count': len(endpoints),
        'source_url': source_url
    }

def get_previous_schema(api_name: str) -> List[Dict]:
    """Get the most recent previous schema for comparison."""
    try:
        response = table.query(
            KeyConditionExpression='api_name = :name',
            ExpressionAttributeValues={':name': api_name},
            ScanIndexForward=False,
            Limit=1
        )
        
        if response['Items']:
            # Get all endpoints for the most recent timestamp
            latest_timestamp = response['Items'][0]['timestamp']
            response = table.query(
                KeyConditionExpression='api_name = :name AND #ts = :timestamp',
                ExpressionAttributeNames={'#ts': 'timestamp'},
                ExpressionAttributeValues={
                    ':name': api_name,
                    ':timestamp': latest_timestamp
                }
            )
            return response['Items']
        return []
    except Exception as e:
        print(f"Error getting previous schema for {api_name}: {e}")
        return []

def compare_schemas(old_schema: List[Dict], new_schema: List[Dict]) -> Dict:
    """Compare old and new schemas to detect changes."""
    changes = {
        'added_endpoints': [],
        'removed_endpoints': [],
        'modified_endpoints': []
    }
    
    # Create sets for easy comparison
    old_endpoints = {(item['endpoint'], item['method']) for item in old_schema}
    new_endpoints = {(item['endpoint'], item['method']) for item in new_schema}
    
    # Find added and removed endpoints
    added = new_endpoints - old_endpoints
    removed = old_endpoints - new_endpoints
    
    changes['added_endpoints'] = [{'path': ep[0], 'method': ep[1]} for ep in added]
    changes['removed_endpoints'] = [{'path': ep[0], 'method': ep[1]} for ep in removed]
    
    # Find modified endpoints (same path/method but different schema)
    common = old_endpoints & new_endpoints
    for endpoint, method in common:
        old_item = next(item for item in old_schema if item['endpoint'] == endpoint and item['method'] == method)
        new_item = next(item for item in new_schema if item['endpoint'] == endpoint and item['method'] == method)
        
        if old_item['schema'] != new_item['schema']:
            changes['modified_endpoints'].append({
                'path': endpoint,
                'method': method,
                'old_schema': old_item['schema'],
                'new_schema': new_item['schema']
            })
    
    return changes

def send_sns_notification(api_name: str, changes: Dict, timestamp: int) -> None:
    """Send SNS notification about schema changes."""
    try:
        message = {
            'api_name': api_name,
            'timestamp': timestamp,
            'changes_summary': {
                'added_count': len(changes['added_endpoints']),
                'removed_count': len(changes['removed_endpoints']),
                'modified_count': len(changes['modified_endpoints'])
            },
            'changes': changes
        }
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message, default=str),
            Subject=f"API Schema Changes Detected: {api_name}"
        )
        print(f"SNS notification sent for {api_name}")
    except Exception as e:
        print(f"Error sending SNS notification: {e}")

def lambda_handler(event, context):
    """Main Lambda handler for scheduled API scanning."""
    print(f"Starting scheduled API scan at {datetime.now()}")
    
    # List of APIs to scan (can be moved to environment variables or DynamoDB)
    apis_to_scan = [
        {
            'name': 'PetStore',
            'url': 'https://petstore.swagger.io/v2/swagger.json'
        },
        {
            'name': 'GitHub',
            'url': 'https://api.github.com/v3/swagger.json'
        }
    ]
    
    scan_results = []
    
    for api in apis_to_scan:
        try:
            print(f"Scanning API: {api['name']}")
            
            # Scrape current schema
            current_endpoints = scrape_openapi(api['url'])
            if not current_endpoints:
                print(f"No endpoints found for {api['name']}, skipping")
                continue
            
            # Store current schema
            snapshot = store_schema_snapshot(api['name'], current_endpoints, api['url'])
            
            # Get previous schema for comparison
            previous_schema = get_previous_schema(api['name'])
            
            if previous_schema:
                # Compare schemas
                changes = compare_schemas(previous_schema, current_endpoints)
                
                # Check if there are any changes
                total_changes = (len(changes['added_endpoints']) + 
                               len(changes['removed_endpoints']) + 
                               len(changes['modified_endpoints']))
                
                if total_changes > 0:
                    print(f"Changes detected in {api['name']}: {total_changes} changes")
                    send_sns_notification(api['name'], changes, snapshot['timestamp'])
                else:
                    print(f"No changes detected in {api['name']}")
            
            scan_results.append({
                'api_name': api['name'],
                'timestamp': snapshot['timestamp'],
                'endpoints_count': snapshot['endpoints_count'],
                'status': 'success'
            })
            
        except Exception as e:
            print(f"Error processing API {api['name']}: {e}")
            scan_results.append({
                'api_name': api['name'],
                'timestamp': int(time.time()),
                'endpoints_count': 0,
                'status': 'error',
                'error': str(e)
            })
    
    # Store scan metadata
    scan_metadata = {
        'scan_id': f"scan_{int(time.time())}",
        'timestamp': int(time.time()),
        'results': scan_results,
        'total_apis_scanned': len(apis_to_scan),
        'successful_scans': len([r for r in scan_results if r['status'] == 'success'])
    }
    
    # Store scan metadata in DynamoDB (optional)
    try:
        metadata_table = dynamodb.Table(os.getenv('SCAN_METADATA_TABLE', 'ApiScanMetadata'))
        metadata_table.put_item(Item=scan_metadata)
    except Exception as e:
        print(f"Error storing scan metadata: {e}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Scheduled API scan completed',
            'scan_results': scan_results,
            'scan_metadata': scan_metadata
        })
    } 