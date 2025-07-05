"""
@file scheduled_scanner.py
@brief Lambda function for scheduled API scanning with EventBridge integration
@author Huy Le (huyisme-005)
@description 
    This Lambda function is triggered by EventBridge daily to scan configured APIs,
    compare schemas with previous versions, and send SNS notifications when changes are detected.
    
    Key Features:
    - Daily automated scanning via EventBridge
    - Detailed schema comparison with diff reporting
    - SNS notifications for schema changes
    - CloudWatch logging for monitoring
    - Retry logic for failed scans
    
    Environment Variables Required:
    - DYNAMODB_SCHEMA_TABLE: DynamoDB table for schema snapshots
    - SCAN_METADATA_TABLE: DynamoDB table for scan metadata
    - SNS_TOPIC_ARN: SNS topic for change notifications
    - ENVIRONMENT: Deployment environment (dev/prod)
    
    Potential Issues:
    - Lambda timeout (300s max)
    - Network connectivity to external APIs
    - DynamoDB throttling
    - SNS delivery failures
    
    Debugging Tips:
    - Check CloudWatch logs for detailed execution info
    - Monitor DynamoDB metrics for throttling
    - Verify SNS topic permissions
    - Test individual API endpoints manually
"""

import json
import boto3
import os
import time
import logging
from datetime import datetime, timezone
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

# Environment variables
SCHEMA_TABLE = os.getenv('DYNAMODB_SCHEMA_TABLE', 'ApiSchemaSnapshots')
METADATA_TABLE = os.getenv('SCAN_METADATA_TABLE', 'ApiScanMetadata')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

# Initialize DynamoDB tables
schema_table = dynamodb.Table(SCHEMA_TABLE)
metadata_table = dynamodb.Table(METADATA_TABLE)

@dataclass
class APIConfig:
    """Configuration for an API to be scanned"""
    name: str
    url: str
    description: str = ""
    retry_count: int = 3
    timeout: int = 30

@dataclass
class ScanResult:
    """Result of scanning a single API"""
    api_name: str
    timestamp: int
    endpoints_count: int
    status: str
    error: Optional[str] = None
    changes_detected: bool = False
    changes_summary: Optional[Dict] = None

class SchemaComparator:
    """
    @class SchemaComparator
    @brief Compares API schemas and generates detailed diff reports
    @description 
        Provides methods to compare two API schema versions and generate
        structured diff reports for SNS notifications and dashboard display.
        
        Methods:
        - compare_schemas: Main comparison method
        - _extract_field_paths: Extract all field paths from schema
        - _generate_diff_summary: Create structured diff summary
    """
    
    @staticmethod
    def compare_schemas(old_schema: List[Dict], new_schema: List[Dict]) -> Dict[str, Any]:
        """
        @method compare_schemas
        @brief Compare old and new schemas to detect changes
        @param old_schema: Previous schema version
        @param new_schema: Current schema version
        @return: Dictionary with detailed change information
        @description
            Compares two schema versions and returns a structured diff report
            including added, removed, and modified endpoints and fields.
        """
        logger.info(f"Comparing schemas: {len(old_schema)} old vs {len(new_schema)} new endpoints")
        
        # Create endpoint maps for comparison
        old_endpoints = {(item['endpoint'], item['method']): item for item in old_schema}
        new_endpoints = {(item['endpoint'], item['method']): item for item in new_schema}
        
        # Find added and removed endpoints
        added_endpoints = new_endpoints.keys() - old_endpoints.keys()
        removed_endpoints = old_endpoints.keys() - new_endpoints.keys()
        common_endpoints = old_endpoints.keys() & new_endpoints.keys()
        
        # Analyze changes in common endpoints
        modified_endpoints = []
        field_changes = {
            'added': {},
            'removed': {},
            'changed': {}
        }
        
        for endpoint_key in common_endpoints:
            old_item = old_endpoints[endpoint_key]
            new_item = new_endpoints[endpoint_key]
            
            if old_item['schema'] != new_item['schema']:
                modified_endpoints.append(endpoint_key)
                
                # Compare field-level changes
                field_diff = SchemaComparator._compare_fields(
                    old_item['schema'], 
                    new_item['schema'], 
                    f"{endpoint_key[1]}:{endpoint_key[0]}"
                )
                
                # Merge field changes
                for change_type in ['added', 'removed', 'changed']:
                    field_changes[change_type].update(field_diff[change_type])
        
        # Generate structured diff summary
        diff_summary = SchemaComparator._generate_diff_summary(
            added_endpoints, removed_endpoints, modified_endpoints, field_changes
        )
        
        return {
            'added_endpoints': [{'path': ep[0], 'method': ep[1]} for ep in added_endpoints],
            'removed_endpoints': [{'path': ep[0], 'method': ep[1]} for ep in removed_endpoints],
            'modified_endpoints': [{'path': ep[0], 'method': ep[1]} for ep in modified_endpoints],
            'field_changes': field_changes,
            'diff_summary': diff_summary,
            'total_changes': len(added_endpoints) + len(removed_endpoints) + len(modified_endpoints)
        }
    
    @staticmethod
    def _compare_fields(old_schema: Dict, new_schema: Dict, endpoint_path: str) -> Dict[str, Dict]:
        """
        @method _compare_fields
        @brief Compare field-level changes in schemas
        @param old_schema: Previous schema
        @param new_schema: Current schema
        @param endpoint_path: Path identifier for the endpoint
        @return: Dictionary of field changes
        @description
            Recursively compares schema fields to detect additions, removals, and modifications.
        """
        old_fields = SchemaComparator._extract_field_paths(old_schema)
        new_fields = SchemaComparator._extract_field_paths(new_schema)
        
        added = {f"{endpoint_path}.{field}": new_fields[field] for field in new_fields - old_fields}
        removed = {f"{endpoint_path}.{field}": old_fields[field] for field in old_fields - new_fields}
        changed = {}
        
        # Check for type changes in common fields
        common_fields = old_fields & new_fields
        for field in common_fields:
            if old_fields[field] != new_fields[field]:
                changed[f"{endpoint_path}.{field}"] = {
                    'old_type': old_fields[field],
                    'new_type': new_fields[field]
                }
        
        return {'added': added, 'removed': removed, 'changed': changed}
    
    @staticmethod
    def _extract_field_paths(schema: Dict, prefix: str = "") -> Dict[str, str]:
        """
        @method _extract_field_paths
        @brief Extract all field paths and their types from a schema
        @param schema: Schema dictionary
        @param prefix: Current path prefix
        @return: Dictionary of field paths to types
        @description
            Recursively traverses schema to extract all field paths and their types.
        """
        fields = {}
        
        if isinstance(schema, dict):
            for key, value in schema.items():
                current_path = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict) and 'type' in value:
                    fields[current_path] = value['type']
                elif isinstance(value, dict):
                    # Recursively extract nested fields
                    nested_fields = SchemaComparator._extract_field_paths(value, current_path)
                    fields.update(nested_fields)
                else:
                    fields[current_path] = str(type(value).__name__)
        
        return fields
    
    @staticmethod
    def _generate_diff_summary(added_endpoints: set, removed_endpoints: set, 
                              modified_endpoints: set, field_changes: Dict) -> Dict[str, Any]:
        """
        @method _generate_diff_summary
        @brief Generate a structured summary of all changes
        @param added_endpoints: Set of added endpoints
        @param removed_endpoints: Set of removed endpoints
        @param modified_endpoints: Set of modified endpoints
        @param field_changes: Dictionary of field-level changes
        @return: Structured diff summary
        @description
            Creates a comprehensive summary of all detected changes for SNS notifications
            and dashboard display.
        """
        return {
            'endpoint_changes': {
                'added': len(added_endpoints),
                'removed': len(removed_endpoints),
                'modified': len(modified_endpoints)
            },
            'field_changes': {
                'added': len(field_changes['added']),
                'removed': len(field_changes['removed']),
                'changed': len(field_changes['changed'])
            },
            'total_changes': (len(added_endpoints) + len(removed_endpoints) + 
                            len(modified_endpoints) + len(field_changes['added']) + 
                            len(field_changes['removed']) + len(field_changes['changed']))
        }

class APIScanner:
    """
    @class APIScanner
    @brief Handles API scraping and schema extraction
    @description 
        Responsible for scraping OpenAPI specifications and extracting
        endpoint information with proper error handling and retry logic.
        
        Methods:
        - scrape_openapi: Main scraping method
        - _extract_auth_type: Extract authentication information
        - _extract_schema: Extract input/output schemas
    """
    
    @staticmethod
    def scrape_openapi(openapi_url: str, timeout: int = 30) -> List[Dict[str, Any]]:
        """
        @method scrape_openapi
        @brief Scrape OpenAPI specification and extract endpoints
        @param openapi_url: URL to the OpenAPI JSON specification
        @param timeout: Request timeout in seconds
        @return: List of endpoint dictionaries
        @description
            Fetches and parses OpenAPI specification to extract endpoint metadata
            including methods, paths, authentication, and schemas.
        """
        try:
            logger.info(f"Scraping OpenAPI from: {openapi_url}")
            response = requests.get(openapi_url, timeout=timeout)
            response.raise_for_status()
            spec = response.json()
            
            endpoints = []
            auth_type = APIScanner._extract_auth_type(spec)
            
            logger.info(f"Found {len(spec.get('paths', {}))} paths in OpenAPI spec")
            
            for path, methods in spec.get('paths', {}).items():
                for method, details in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        endpoint = {
                            'method': method.upper(),
                            'path': path,
                            'auth_type': auth_type,
                            'input_schema': APIScanner._extract_schema(details, 'requestBody', spec),
                            'output_schema': APIScanner._extract_schema(details, 'responses', spec)
                        }
                        endpoints.append(endpoint)
            
            logger.info(f"Extracted {len(endpoints)} endpoints from {openapi_url}")
            return endpoints
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error scraping {openapi_url}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in OpenAPI spec {openapi_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping {openapi_url}: {e}")
            raise
    
    @staticmethod
    def _extract_auth_type(spec: Dict) -> str:
        """
        @method _extract_auth_type
        @brief Extract authentication type from OpenAPI spec
        @param spec: OpenAPI specification dictionary
        @return: Authentication type string
        """
        security_schemes = spec.get('components', {}).get('securitySchemes', {})
        
        if not security_schemes:
            return 'none'
        
        auth_types = []
        for scheme_name, scheme_details in security_schemes.items():
            scheme_type = scheme_details.get('type', 'unknown')
            if scheme_type == 'http':
                auth_types.append(f"http_{scheme_details.get('scheme', 'unknown')}")
            elif scheme_type == 'apiKey':
                auth_types.append('api_key')
            elif scheme_type == 'oauth2':
                auth_types.append('oauth2')
            else:
                auth_types.append(scheme_type)
        
        return ', '.join(auth_types) if auth_types else 'none'
    
    @staticmethod
    def _extract_schema(details: Dict, schema_type: str, spec: Dict) -> Dict[str, Any]:
        """
        @method _extract_schema
        @brief Extract input or output schema from endpoint details
        @param details: Endpoint details dictionary
        @param schema_type: Type of schema ('requestBody' or 'responses')
        @param spec: Full OpenAPI specification
        @return: Extracted schema dictionary
        """
        if schema_type == 'requestBody':
            request_body = details.get('requestBody', {})
            if not request_body:
                return {'type': 'none', 'description': 'No request body required'}
            
            content = request_body.get('content', {})
            for content_type in ['application/json', 'application/x-www-form-urlencoded']:
                if content_type in content:
                    return {
                        'content_type': content_type,
                        'schema': content[content_type].get('schema', {}),
                        'required': request_body.get('required', False)
                    }
            
            return {'type': 'unknown', 'description': 'Request body present but schema unclear'}
        
        elif schema_type == 'responses':
            responses = details.get('responses', {})
            if not responses:
                return {'type': 'none', 'description': 'No response schema defined'}
            
            # Look for success responses
            for code in ['200', '201', '202', '204']:
                if code in responses:
                    response = responses[code]
                    content = response.get('content', {})
                    
                    for content_type in ['application/json', 'application/xml']:
                        if content_type in content:
                            return {
                                'content_type': content_type,
                                'schema': content[content_type].get('schema', {}),
                                'status_code': code
                            }
            
            return {'type': 'unknown', 'description': 'Response present but schema unclear'}

class DynamoDBManager:
    """
    @class DynamoDBManager
    @brief Manages DynamoDB operations for schema storage and retrieval
    @description 
        Handles all DynamoDB operations including storing schema snapshots,
        retrieving previous versions, and managing scan metadata.
        
        Methods:
        - store_schema_snapshot: Store current schema
        - get_previous_schema: Retrieve previous schema version
        - store_scan_metadata: Store scan execution metadata
    """
    
    @staticmethod
    def store_schema_snapshot(api_name: str, endpoints: List[Dict], source_url: str) -> Dict:
        """
        @method store_schema_snapshot
        @brief Store current schema snapshot in DynamoDB
        @param api_name: Name of the API
        @param endpoints: List of endpoint dictionaries
        @param source_url: Source URL of the API specification
        @return: Snapshot metadata
        @description
            Stores each endpoint as a separate item in DynamoDB with timestamp
            for versioning and comparison.
        """
        timestamp = int(time.time())
        stored_count = 0
        
        try:
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
                schema_table.put_item(Item=item)
                stored_count += 1
            
            logger.info(f"Stored {stored_count} endpoints for {api_name} at timestamp {timestamp}")
            
            return {
                'api_name': api_name,
                'timestamp': timestamp,
                'endpoints_count': len(endpoints),
                'stored_count': stored_count,
                'source_url': source_url
            }
            
        except Exception as e:
            logger.error(f"Error storing schema snapshot for {api_name}: {e}")
            raise
    
    @staticmethod
    def get_previous_schema(api_name: str) -> List[Dict]:
        """
        @method get_previous_schema
        @brief Get the most recent previous schema for comparison
        @param api_name: Name of the API
        @return: List of previous schema items
        @description
            Retrieves the most recent schema version from DynamoDB for comparison
            with the current scan results.
        """
        try:
            # Get the most recent timestamp for this API
            response = schema_table.query(
                KeyConditionExpression='api_name = :name',
                ExpressionAttributeValues={':name': api_name},
                ScanIndexForward=False,
                Limit=1
            )
            
            if not response['Items']:
                logger.info(f"No previous schema found for {api_name}")
                return []
            
            # Get all endpoints for the most recent timestamp
            latest_timestamp = response['Items'][0]['timestamp']
            response = schema_table.query(
                KeyConditionExpression='api_name = :name AND #ts = :timestamp',
                ExpressionAttributeNames={'#ts': 'timestamp'},
                ExpressionAttributeValues={
                    ':name': api_name,
                    ':timestamp': latest_timestamp
                }
            )
            
            logger.info(f"Retrieved {len(response['Items'])} previous endpoints for {api_name}")
            return response['Items']
            
        except Exception as e:
            logger.error(f"Error getting previous schema for {api_name}: {e}")
            return []
    
    @staticmethod
    def store_scan_metadata(scan_metadata: Dict) -> None:
        """
        @method store_scan_metadata
        @brief Store scan execution metadata
        @param scan_metadata: Scan metadata dictionary
        @description
            Stores metadata about the scan execution including results,
            timestamps, and success/failure counts.
        """
        try:
            metadata_table.put_item(Item=scan_metadata)
            logger.info(f"Stored scan metadata: {scan_metadata['scan_id']}")
        except Exception as e:
            logger.error(f"Error storing scan metadata: {e}")

class SNSNotifier:
    """
    @class SNSNotifier
    @brief Handles SNS notifications for schema changes
    @description 
        Manages SNS notifications when schema changes are detected,
        including message formatting and delivery confirmation.
        
        Methods:
        - send_change_notification: Send notification about changes
        - format_change_message: Format change details for SNS
    """
    
    @staticmethod
    def send_change_notification(api_name: str, changes: Dict, timestamp: int) -> bool:
        """
        @method send_change_notification
        @brief Send SNS notification about schema changes
        @param api_name: Name of the API with changes
        @param changes: Dictionary containing change details
        @param timestamp: Timestamp of the scan
        @return: True if notification sent successfully
        @description
            Formats and sends an SNS notification when schema changes are detected.
            Includes detailed diff information and metadata.
        """
        try:
            if not SNS_TOPIC_ARN:
                logger.warning("SNS_TOPIC_ARN not configured, skipping notification")
                return False
            
            message = SNSNotifier.format_change_message(api_name, changes, timestamp)
            
            response = sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps(message, default=str),
                Subject=f"API Schema Changes Detected: {api_name}",
                MessageAttributes={
                    'event_type': {
                        'DataType': 'String',
                        'StringValue': 'api.schema.updated'
                    },
                    'api_name': {
                        'DataType': 'String',
                        'StringValue': api_name
                    },
                    'environment': {
                        'DataType': 'String',
                        'StringValue': ENVIRONMENT
                    }
                }
            )
            
            logger.info(f"SNS notification sent for {api_name}: {response['MessageId']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SNS notification for {api_name}: {e}")
            return False
    
    @staticmethod
    def format_change_message(api_name: str, changes: Dict, timestamp: int) -> Dict[str, Any]:
        """
        @method format_change_message
        @brief Format change details for SNS notification
        @param api_name: Name of the API
        @param changes: Change details dictionary
        @param timestamp: Scan timestamp
        @return: Formatted message dictionary
        @description
            Creates a structured message for SNS notification including
            event metadata, change summary, and detailed diff information.
        """
        return {
            'event': 'api.schema.updated',
            'api': api_name,
            'timestamp': datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(),
            'environment': ENVIRONMENT,
            'diff_summary': changes['diff_summary'],
            'changes': {
                'added_endpoints': changes['added_endpoints'],
                'removed_endpoints': changes['removed_endpoints'],
                'modified_endpoints': changes['modified_endpoints'],
                'field_changes': changes['field_changes']
            },
            'metadata': {
                'scan_timestamp': timestamp,
                'total_changes': changes['total_changes']
            }
        }

def lambda_handler(event, context):
    """
    @function lambda_handler
    @brief Main Lambda handler for scheduled API scanning
    @param event: EventBridge event
    @param context: Lambda context
    @return: Response dictionary
    @description
        Main entry point for the Lambda function. Handles EventBridge triggers,
        orchestrates API scanning, schema comparison, and notifications.
        
        Process Flow:
        1. Parse EventBridge event
        2. Load API configurations
        3. Scan each API
        4. Compare with previous versions
        5. Send notifications for changes
        6. Store scan metadata
        7. Return execution summary
        
        Error Handling:
        - Individual API failures don't stop the entire scan
        - Retry logic for transient failures
        - Comprehensive logging for debugging
        - Graceful degradation for missing dependencies
    """
    start_time = time.time()
    logger.info(f"Starting scheduled API scan at {datetime.now()}")
    logger.info(f"Event: {json.dumps(event)}")
    
    # Configure APIs to scan (can be moved to DynamoDB or environment variables)
    apis_to_scan = [
        APIConfig(
            name='PetStore',
            url='https://petstore.swagger.io/v2/swagger.json',
            description='Swagger Petstore API'
        ),
        APIConfig(
            name='GitHub',
            url='https://api.github.com/v3/swagger.json',
            description='GitHub REST API'
        ),
        APIConfig(
            name='Shopify',
            url='https://shopify.dev/api/admin-rest/2023-07/openapi.json',
            description='Shopify Admin API'
        )
    ]
    
    scan_results = []
    total_changes = 0
    
    for api_config in apis_to_scan:
        result = ScanResult(
            api_name=api_config.name,
            timestamp=int(time.time()),
            endpoints_count=0,
            status='pending'
        )
        
        try:
            logger.info(f"Scanning API: {api_config.name} from {api_config.url}")
            
            # Scrape current schema with retry logic
            current_endpoints = None
            for attempt in range(api_config.retry_count):
                try:
                    current_endpoints = APIScanner.scrape_openapi(
                        api_config.url, 
                        timeout=api_config.timeout
                    )
                    break
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {api_config.name}: {e}")
                    if attempt == api_config.retry_count - 1:
                        raise
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            if not current_endpoints:
                logger.warning(f"No endpoints found for {api_config.name}, skipping")
                result.status = 'error'
                result.error = 'No endpoints found'
                scan_results.append(result)
                continue
            
            # Store current schema
            snapshot = DynamoDBManager.store_schema_snapshot(
                api_config.name, 
                current_endpoints, 
                api_config.url
            )
            
            # Get previous schema for comparison
            previous_schema = DynamoDBManager.get_previous_schema(api_config.name)
            
            if previous_schema:
                # Compare schemas
                changes = SchemaComparator.compare_schemas(previous_schema, current_endpoints)
                
                # Check if there are any changes
                if changes['total_changes'] > 0:
                    logger.info(f"Changes detected in {api_config.name}: {changes['total_changes']} changes")
                    
                    # Send SNS notification
                    notification_sent = SNSNotifier.send_change_notification(
                        api_config.name, 
                        changes, 
                        snapshot['timestamp']
                    )
                    
                    result.changes_detected = True
                    result.changes_summary = changes['diff_summary']
                    total_changes += changes['total_changes']
                    
                    logger.info(f"SNS notification {'sent' if notification_sent else 'failed'} for {api_config.name}")
                else:
                    logger.info(f"No changes detected in {api_config.name}")
            else:
                logger.info(f"No previous schema found for {api_config.name}, storing initial version")
            
            # Update result
            result.status = 'success'
            result.endpoints_count = snapshot['endpoints_count']
            result.timestamp = snapshot['timestamp']
            
        except Exception as e:
            logger.error(f"Error processing API {api_config.name}: {e}")
            result.status = 'error'
            result.error = str(e)
        
        scan_results.append(result)
    
    # Store scan metadata
    scan_metadata = {
        'scan_id': f"scan_{int(time.time())}",
        'timestamp': int(time.time()),
        'event_source': event.get('source', 'unknown'),
        'results': [asdict(result) for result in scan_results],
        'total_apis_scanned': len(apis_to_scan),
        'successful_scans': len([r for r in scan_results if r.status == 'success']),
        'total_changes_detected': total_changes,
        'execution_time_seconds': time.time() - start_time,
        'environment': ENVIRONMENT
    }
    
    try:
        DynamoDBManager.store_scan_metadata(scan_metadata)
    except Exception as e:
        logger.error(f"Error storing scan metadata: {e}")
    
    # Log final summary
    logger.info(f"Scan completed in {time.time() - start_time:.2f} seconds")
    logger.info(f"APIs scanned: {len(apis_to_scan)}")
    logger.info(f"Successful scans: {scan_metadata['successful_scans']}")
    logger.info(f"Total changes detected: {total_changes}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Scheduled API scan completed successfully',
            'scan_metadata': scan_metadata,
            'scan_results': [asdict(result) for result in scan_results]
        }, default=str)
    } 