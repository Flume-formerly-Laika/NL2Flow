"""
Pytest configuration file for NL2Flow tests.
This file configures pytest behavior and handles warnings.
"""

import pytest
import warnings
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure warnings
def pytest_configure(config):
    """Configure pytest and handle warnings."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: Unit tests for basic functionality"
    )
    config.addinivalue_line(
        "markers", "dynamodb: Tests for DynamoDB management features"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    
    # Filter out deprecation warnings from dependencies
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module="botocore.*"
    )
    warnings.filterwarnings(
        "ignore", 
        category=DeprecationWarning,
        module="httpx.*"
    )
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        module="httpx.*"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to basic functionality tests
        if any(name in item.name for name in ["health", "parse_request", "openapi", "html"]):
            item.add_marker(pytest.mark.unit)
        
        # Add dynamodb marker to DynamoDB-related tests
        if any(name in item.name for name in ["dynamodb", "list_apis", "list_versions", "delete_api", "delete_snapshot", "schema_snapshot"]):
            item.add_marker(pytest.mark.dynamodb)
        
        # Add integration marker to complex tests
        if any(name in item.name for name in ["diff_engine", "schema_diff"]):
            item.add_marker(pytest.mark.integration) 