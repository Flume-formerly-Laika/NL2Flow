import boto3
import os
import time
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import json

# DynamoDB table name (can be set via env var for flexibility)
DYNAMODB_TABLE = os.getenv("DYNAMODB_SCHEMA_TABLE", "ApiSchemaSnapshots")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE)

def store_schema_snapshot(api_name, endpoint, method, schema, metadata=None, timestamp=None):
    """
    Store a schema snapshot in DynamoDB with a versioned timestamp.
    """
    if timestamp is None:
        import time
        timestamp = int(time.time())
    item = {
        "api_name": api_name,
        "endpoint": endpoint,
        "method": method.upper(),
        "timestamp": str(timestamp),
        "schema": json.loads(json.dumps(schema), parse_float=Decimal),
        "metadata": metadata or {},
    }
    table.put_item(Item=item)
    return item

def get_schema_snapshots(api_name, endpoint=None, method=None):
    """
    Retrieve all schema snapshots for an API, optionally filtered by endpoint and method.
    """
    key_expr = Key("api_name").eq(api_name)
    if endpoint:
        key_expr = key_expr & Key("endpoint").eq(endpoint)
    if method:
        key_expr = key_expr & Key("method").eq(method.upper())
    response = table.query(
        KeyConditionExpression=key_expr
    )
    return response.get("Items", [])

def get_schema_by_version(api_name, timestamp, endpoint=None, method=None):
    """
    Retrieve a specific schema snapshot by API name and timestamp, optionally filtered by endpoint and method.
    """
    key_expr = Key("api_name").eq(api_name) & Key("timestamp").eq(str(timestamp))
    if endpoint:
        key_expr = key_expr & Key("endpoint").eq(endpoint)
    if method:
        key_expr = key_expr & Key("method").eq(method.upper())
    response = table.query(
        KeyConditionExpression=key_expr
    )
    items = response.get("Items", [])
    return items[0] if items else None

def update_schema_snapshot(api_name, endpoint, method, schema, metadata=None, timestamp=None):
    """
    Update (overwrite) a schema snapshot for a given API, endpoint, method, and timestamp.
    If timestamp is None, use the current time.
    """
    return store_schema_snapshot(api_name, endpoint, method, schema, metadata, timestamp) 