#!/usr/bin/env python3
"""
test_schema_extraction.py
-------------------------
Test script to demonstrate the enhanced API doc scraper with improved schema extraction.

This script shows how to:
1. Test OpenAPI scraping with detailed debugging
2. Validate extraction quality
3. Debug specific endpoints
4. Compare different API specs

Usage:
    python test_schema_extraction.py
"""

import sys
import os
import json
import logging

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.api_doc_scraper import (
    scrape_openapi, 
    scrape_html_doc, 
    debug_schema_extraction, 
    validate_schema_extraction
)

def test_openapi_scraping():
    """Test OpenAPI scraping with a well-known API spec."""
    print("🔍 Testing OpenAPI Scraping")
    print("=" * 50)
    
    # Test with Shopify's OpenAPI (well-structured)
    shopify_url = "https://shopify.dev/api/admin-rest/2023-10/openapi.json"
    
    try:
        print(f"📡 Scraping: {shopify_url}")
        endpoints = scrape_openapi(shopify_url)
        
        print(f"✅ Successfully extracted {len(endpoints)} endpoints")
        
        # Validate extraction quality
        validation = validate_schema_extraction(endpoints)
        print(f"📊 Extraction Quality:")
        print(f"   Auth detection: {validation['auth_detection_rate']}")
        print(f"   Input schema: {validation['input_schema_rate']}")
        print(f"   Output schema: {validation['output_schema_rate']}")
        
        # Show sample endpoints
        print(f"\n📋 Sample Endpoints:")
        for i, ep in enumerate(endpoints[:3]):
            print(f"\n{i+1}. {ep['method']} {ep['path']}")
            print(f"   Auth: {ep['auth_type']}")
            print(f"   Input: {ep['input_schema'].get('type', 'unknown')}")
            print(f"   Output: {ep['output_schema'].get('type', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_html_scraping():
    """Test HTML scraping with a documentation page."""
    print("\n🔍 Testing HTML Scraping")
    print("=" * 50)
    
    # Test with a simple HTML page (you can replace with actual API docs)
    test_url = "https://httpbin.org/json"  # Simple JSON endpoint for testing
    
    try:
        print(f"📡 Scraping: {test_url}")
        endpoints = scrape_html_doc(test_url)
        
        print(f"✅ Successfully extracted {len(endpoints)} endpoints")
        
        # Validate extraction quality
        validation = validate_schema_extraction(endpoints)
        print(f"📊 Extraction Quality:")
        print(f"   Auth detection: {validation['auth_detection_rate']}")
        print(f"   Input schema: {validation['input_schema_rate']}")
        print(f"   Output schema: {validation['output_schema_rate']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_debug_function():
    """Test the debug function for detailed analysis."""
    print("\n🔍 Testing Debug Function")
    print("=" * 50)
    
    # Test with a smaller OpenAPI spec
    test_url = "https://petstore.swagger.io/v2/swagger.json"
    
    try:
        print(f"📡 Debugging: {test_url}")
        debug_schema_extraction(test_url)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_schema_validation():
    """Test schema validation with sample data."""
    print("\n🔍 Testing Schema Validation")
    print("=" * 50)
    
    # Sample endpoints with different quality levels
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
    print(f"📊 Validation Results:")
    print(f"   Total endpoints: {validation['total_endpoints']}")
    print(f"   Auth detection: {validation['auth_detection_rate']}")
    print(f"   Input schema: {validation['input_schema_rate']}")
    print(f"   Output schema: {validation['output_schema_rate']}")
    
    # Use json to pretty-print the full validation results
    print(f"\n📋 Full Validation Details:")
    print(json.dumps(validation, indent=2))
    
    if validation['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in validation['recommendations']:
            print(f"   {rec}")
    
    return True

def main():
    """Run all tests."""
    print("🚀 API Doc Scraper - Enhanced Schema Extraction Test")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run tests
    tests = [
        ("OpenAPI Scraping", test_openapi_scraping),
        ("HTML Scraping", test_html_scraping),
        ("Debug Function", test_debug_function),
        ("Schema Validation", test_schema_validation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Schema extraction is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\n💡 Debugging Tips:")
        print("1. Check network connectivity")
        print("2. Verify API URLs are accessible")
        print("3. Use debug_schema_extraction() for detailed analysis")
        print("4. Check if OpenAPI specs are valid JSON")

if __name__ == "__main__":
    main() 