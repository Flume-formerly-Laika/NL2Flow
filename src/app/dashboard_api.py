"""
Admin Dashboard API endpoints for NL2Flow Watchdog and Alerting system.
Provides endpoints for viewing scan history, detected changes, and triggering rescans.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import boto3
import os
from datetime import datetime, timezone
import time
from pydantic import BaseModel

from utils.dynamodb_snapshots import get_schema_by_version
from utils.schema_diff import diff_schema_versions
from api_doc_scraper import scrape_openapi

router = APIRouter(prefix="/dashboard", tags=["Admin Dashboard"])

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
schema_table = dynamodb.Table(os.getenv('DYNAMODB_SCHEMA_TABLE', 'ApiSchemaSnapshots'))
metadata_table = dynamodb.Table(os.getenv('SCAN_METADATA_TABLE', 'ApiScanMetadata'))

# Pydantic models
class ScanResult(BaseModel):
    api_name: str
    timestamp: int
    endpoints_count: int
    status: str
    error: Optional[str] = None

class ScanMetadata(BaseModel):
    scan_id: str
    timestamp: int
    results: List[ScanResult]
    total_apis_scanned: int
    successful_scans: int

class ApiChangeSummary(BaseModel):
    api_name: str
    last_scan_timestamp: int
    last_scan_status: str
    total_endpoints: int
    recent_changes: Dict[str, int]  # added, removed, modified counts
    last_change_timestamp: Optional[int] = None

class RescanRequest(BaseModel):
    api_name: str
    openapi_url: str

class RescanResponse(BaseModel):
    api_name: str
    timestamp: int
    endpoints_count: int
    changes_detected: bool
    changes_summary: Dict[str, int]

@router.get("/scan-history", response_model=List[ScanMetadata])
async def get_scan_history(limit: int = Query(10, ge=1, le=100)):
    """Get recent scan history with metadata."""
    try:
        response = metadata_table.scan(
            Limit=limit,
            ScanIndexForward=False
        )
        
        scan_history = []
        for item in response.get('Items', []):
            scan_history.append(ScanMetadata(**item))
        
        # Sort by timestamp descending
        scan_history.sort(key=lambda x: x.timestamp, reverse=True)
        return scan_history[:limit]
        
    except Exception as e:
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            raise HTTPException(status_code=503, detail="AWS credentials not configured")
        elif "ResourceNotFoundException" in str(e):
            raise HTTPException(status_code=404, detail="Scan metadata table not found")
        else:
            raise HTTPException(status_code=500, detail=f"Error retrieving scan history: {str(e)}")

@router.get("/api-summary", response_model=List[ApiChangeSummary])
async def get_api_summary():
    """Get summary of all APIs with their last scan info and recent changes."""
    try:
        # Get all unique API names
        response = schema_table.scan(
            ProjectionExpression='api_name',
            Select='SPECIFIC_ATTRIBUTES'
        )
        
        api_names = set()
        for item in response.get('Items', []):
            api_names.add(item['api_name'])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = schema_table.scan(
                ProjectionExpression='api_name',
                Select='SPECIFIC_ATTRIBUTES',
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            for item in response.get('Items', []):
                api_names.add(item['api_name'])
        
        api_summaries = []
        
        for api_name in api_names:
            try:
                # Get the most recent scan for this API
                response = schema_table.query(
                    KeyConditionExpression='api_name = :name',
                    ExpressionAttributeValues={':name': api_name},
                    ScanIndexForward=False,
                    Limit=1
                )
                
                if not response.get('Items'):
                    continue
                
                latest_item = response['Items'][0]
                last_scan_timestamp = int(latest_item['timestamp'])
                
                # Get all endpoints for the latest scan
                response = schema_table.query(
                    KeyConditionExpression='api_name = :name AND #ts = :timestamp',
                    ExpressionAttributeNames={'#ts': 'timestamp'},
                    ExpressionAttributeValues={
                        ':name': api_name,
                        ':timestamp': latest_item['timestamp']
                    }
                )
                
                total_endpoints = len(response.get('Items', []))
                
                # Get the previous scan for comparison
                response = schema_table.query(
                    KeyConditionExpression='api_name = :name',
                    ExpressionAttributeValues={':name': api_name},
                    ScanIndexForward=False,
                    Limit=2
                )
                
                recent_changes = {'added': 0, 'removed': 0, 'modified': 0}
                last_change_timestamp = None
                
                if len(response.get('Items', [])) > 1:
                    # Compare with previous scan
                    current_items = [item for item in response['Items'] if item['timestamp'] == latest_item['timestamp']]
                    previous_timestamp = None
                    
                    for item in response['Items']:
                        if item['timestamp'] != latest_item['timestamp']:
                            previous_timestamp = item['timestamp']
                            break
                    
                    if previous_timestamp:
                        # Get previous scan items
                        prev_response = schema_table.query(
                            KeyConditionExpression='api_name = :name AND #ts = :timestamp',
                            ExpressionAttributeNames={'#ts': 'timestamp'},
                            ExpressionAttributeValues={
                                ':name': api_name,
                                ':timestamp': previous_timestamp
                            }
                        )
                        
                        previous_items = prev_response.get('Items', [])
                        
                        # Compare schemas
                        changes = compare_schemas(previous_items, current_items)
                        recent_changes = {
                            'added': len(changes['added_endpoints']),
                            'removed': len(changes['removed_endpoints']),
                            'modified': len(changes['modified_endpoints'])
                        }
                        
                        if any(recent_changes.values()):
                            last_change_timestamp = last_scan_timestamp
                
                # Get scan status from metadata
                scan_status = "success"  # Default
                try:
                    metadata_response = metadata_table.scan(
                        FilterExpression='contains(results, :api_result)',
                        ExpressionAttributeValues={
                            ':api_result': {'api_name': api_name}
                        },
                        ScanIndexForward=False,
                        Limit=1
                    )
                    
                    if metadata_response.get('Items'):
                        for result in metadata_response['Items'][0].get('results', []):
                            if result.get('api_name') == api_name:
                                scan_status = result.get('status', 'unknown')
                                break
                except:
                    pass  # Use default status if metadata not available
                
                api_summaries.append(ApiChangeSummary(
                    api_name=api_name,
                    last_scan_timestamp=last_scan_timestamp,
                    last_scan_status=scan_status,
                    total_endpoints=total_endpoints,
                    recent_changes=recent_changes,
                    last_change_timestamp=last_change_timestamp
                ))
                
            except Exception as e:
                print(f"Error processing API {api_name}: {e}")
                continue
        
        # Sort by last scan timestamp descending
        api_summaries.sort(key=lambda x: x.last_scan_timestamp, reverse=True)
        return api_summaries
        
    except Exception as e:
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            raise HTTPException(status_code=503, detail="AWS credentials not configured")
        elif "ResourceNotFoundException" in str(e):
            raise HTTPException(status_code=404, detail="Schema table not found")
        else:
            raise HTTPException(status_code=500, detail=f"Error retrieving API summary: {str(e)}")

@router.post("/rescan-api", response_model=RescanResponse)
async def rescan_api(request: RescanRequest):
    """Trigger a manual rescan of a specific API."""
    try:
        # Scrape current schema
        try:
            current_endpoints = scrape_openapi(request.openapi_url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid OpenAPI URL: {str(e)}")
        if not current_endpoints:
            raise HTTPException(status_code=400, detail=f"Invalid OpenAPI URL or no endpoints found for {request.api_name}")
        
        # Store current schema
        timestamp = int(time.time())
        for endpoint in current_endpoints:
            item = {
                'api_name': request.api_name,
                'endpoint': endpoint['path'],
                'method': endpoint['method'],
                'timestamp': str(timestamp),
                'schema': {
                    'input': endpoint['input_schema'],
                    'output': endpoint['output_schema']
                },
                'metadata': {
                    'auth_type': endpoint['auth_type'],
                    'source_url': request.openapi_url,
                    'version_ts': datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
                }
            }
            schema_table.put_item(Item=item)
        
        # Get previous schema for comparison
        response = schema_table.query(
            KeyConditionExpression='api_name = :name',
            ExpressionAttributeValues={':name': request.api_name},
            ScanIndexForward=False,
            Limit=1
        )
        
        changes_detected = False
        changes_summary = {'added': 0, 'removed': 0, 'modified': 0}
        
        if response.get('Items'):
            # Get all endpoints for the most recent previous scan
            latest_timestamp = response['Items'][0]['timestamp']
            prev_response = schema_table.query(
                KeyConditionExpression='api_name = :name AND #ts = :timestamp',
                ExpressionAttributeNames={'#ts': 'timestamp'},
                ExpressionAttributeValues={
                    ':name': request.api_name,
                    ':timestamp': latest_timestamp
                }
            )
            
            previous_items = prev_response.get('Items', [])
            
            # Compare schemas
            changes = compare_schemas(previous_items, current_endpoints)
            changes_summary = {
                'added': len(changes['added_endpoints']),
                'removed': len(changes['removed_endpoints']),
                'modified': len(changes['modified_endpoints'])
            }
            
            changes_detected = any(changes_summary.values())
        
        return RescanResponse(
            api_name=request.api_name,
            timestamp=timestamp,
            endpoints_count=len(current_endpoints),
            changes_detected=changes_detected,
            changes_summary=changes_summary
        )
        
    except Exception as e:
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            raise HTTPException(status_code=503, detail="AWS credentials not configured")
        elif "ResourceNotFoundException" in str(e):
            raise HTTPException(status_code=404, detail="Schema table not found")
        else:
            raise HTTPException(status_code=500, detail=f"Error rescanning API: {str(e)}")

@router.get("/api-changes/{api_name}")
async def get_api_changes(api_name: str, limit: int = Query(10, ge=1, le=50)):
    """Get detailed change history for a specific API."""
    try:
        # Get all scans for this API
        response = schema_table.query(
            KeyConditionExpression='api_name = :name',
            ExpressionAttributeValues={':name': api_name},
            ScanIndexForward=False
        )
        
        scans = []
        timestamps = set()
        
        for item in response.get('Items', []):
            timestamps.add(item['timestamp'])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = schema_table.query(
                KeyConditionExpression='api_name = :name',
                ExpressionAttributeValues={':name': api_name},
                ScanIndexForward=False,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            for item in response.get('Items', []):
                timestamps.add(item['timestamp'])
        
        # Sort timestamps descending and take the limit
        sorted_timestamps = sorted(timestamps, reverse=True)[:limit]
        
        for timestamp in sorted_timestamps:
            # Get all endpoints for this timestamp
            response = schema_table.query(
                KeyConditionExpression='api_name = :name AND #ts = :timestamp',
                ExpressionAttributeNames={'#ts': 'timestamp'},
                ExpressionAttributeValues={
                    ':name': api_name,
                    ':timestamp': timestamp
                }
            )
            
            scan_data = {
                'timestamp': int(timestamp),
                'endpoints_count': len(response.get('Items', [])),
                'endpoints': response.get('Items', [])
            }
            
            scans.append(scan_data)
        
        return {
            'api_name': api_name,
            'scans': scans,
            'total_scans': len(scans)
        }
        
    except Exception as e:
        if "NoCredentialsError" in str(e) or "botocore.exceptions" in str(e):
            raise HTTPException(status_code=503, detail="AWS credentials not configured")
        elif "ResourceNotFoundException" in str(e):
            raise HTTPException(status_code=404, detail="Schema table not found")
        else:
            raise HTTPException(status_code=500, detail=f"Error retrieving API changes: {str(e)}")

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