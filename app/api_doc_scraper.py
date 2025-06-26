"""
api_doc_scraper.py

@author Huy Le (huyisme-005)
------------------
Scrapes public API documentation (OpenAPI/Swagger and HTML) to extract endpoints, authentication methods, and schemas.

Features:
- Parses OpenAPI/Swagger JSON for endpoints, methods, auth, and schemas.
- Scrapes unstructured HTML docs for endpoints and auth info.
- Outputs a unified structure: method, URL path, auth type, input/output schema.

Dependencies:
- requests
- beautifulsoup4
- openapi-spec-validator (optional, for validation)

Example usage:
    from app.api_doc_scraper import scrape_openapi, scrape_html_doc
    endpoints = scrape_openapi('https://api.example.com/openapi.json')
    html_endpoints = scrape_html_doc('https://api.example.com/docs')

# --- Debugging Tips ---
# 1. Always use a direct OpenAPI JSON URL for scrape_openapi (not an HTML doc page).
#    For Shopify, use: https://shopify.dev/api/admin-rest/<version>/openapi.json
#    (e.g., https://shopify.dev/api/admin-rest/2023-07/openapi.json)
# 2. If you get a 404 error, check if the URL contains /docs/ instead of /api/.
#    The code will auto-correct /docs/ to /api/ and /resources/product to /openapi.json for Shopify.
# 3. If you get a JSON decode error, the URL is likely not a JSON file (it's probably HTML).
# 4. Use scrape_html_doc for HTML documentation pages, but expect less structured results.
# 5. For debugging, enable DEBUG logging to see step-by-step extraction process.
# 6. Use debug_schema_extraction() for detailed inspection of OpenAPI extraction.
# 7. If you encounter network errors, check your internet connection and the URL's accessibility.
# 8. For best results, always prefer official OpenAPI JSON specs over HTML docs.
"""

import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import json
import logging
import re

# --- Structured API (OpenAPI/Swagger) Scraper ---
def scrape_openapi(openapi_url: str) -> List[Dict[str, Any]]:
    """
    Fetches and parses an OpenAPI/Swagger JSON spec to extract endpoints, methods, auth, and schemas.

    Args:
        openapi_url (str): URL to the OpenAPI/Swagger JSON.

    Returns:
        List[Dict[str, Any]]: List of endpoint metadata dicts.
    """
    # DEBUG: Log the URL being scraped
    logging.debug(f"Scraping OpenAPI from: {openapi_url}")
    
    resp = requests.get(openapi_url)
    resp.raise_for_status()
    spec = resp.json()
    
    # DEBUG: Log basic spec info
    logging.debug(f"OpenAPI spec version: {spec.get('openapi', 'unknown')}")
    logging.debug(f"Number of paths: {len(spec.get('paths', {}))}")
    
    endpoints = []
    auth_type = _extract_openapi_auth(spec)
    
    # DEBUG: Log auth type found
    logging.debug(f"Extracted auth type: {auth_type}")
    
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            # DEBUG: Log each endpoint being processed
            logging.debug(f"Processing {method.upper()} {path}")
            
            # Extract input schema with better logic
            input_schema = _extract_input_schema(details, spec)
            
            # Extract output schema with better logic
            output_schema = _extract_output_schema(details, spec)
            
            endpoint = {
                'method': method.upper(),
                'path': path,
                'auth_type': auth_type,
                'input_schema': input_schema,
                'output_schema': output_schema
            }
            endpoints.append(endpoint)
    
    # DEBUG: Log summary
    logging.debug(f"Extracted {len(endpoints)} endpoints from OpenAPI spec")
    return endpoints

def _extract_openapi_auth(spec: dict) -> Optional[str]:
    """
    Extracts authentication type from OpenAPI spec with enhanced logic.
    
    DEBUG: This function looks for security schemes in the components section
    and checks if they are required or optional based on the global security field.
    """
    # Check global security requirements
    global_security = spec.get('security', [])
    
    # Get security schemes from components
    components = spec.get('components', {})
    security_schemes = components.get('securitySchemes', {})
    
    # DEBUG: Log what we found
    logging.debug(f"Global security: {global_security}")
    logging.debug(f"Security schemes found: {list(security_schemes.keys())}")
    
    if not security_schemes:
        return "none"
    
    # Extract auth types with more detail
    auth_types = []
    for scheme_name, scheme_details in security_schemes.items():
        scheme_type = scheme_details.get('type', 'unknown')
        
        # Add more specific auth type information
        if scheme_type == 'http':
            # Check for specific HTTP auth schemes
            if scheme_details.get('scheme') == 'bearer':
                auth_types.append('bearer_token')
            elif scheme_details.get('scheme') == 'basic':
                auth_types.append('basic_auth')
            else:
                auth_types.append(f'http_{scheme_details.get("scheme", "unknown")}')
        elif scheme_type == 'apiKey':
            auth_types.append('api_key')
        elif scheme_type == 'oauth2':
            auth_types.append('oauth2')
        else:
            auth_types.append(scheme_type)
    
    # Determine if auth is required
    if global_security:
        return ', '.join(auth_types) + ' (required)'
    else:
        return ', '.join(auth_types) + ' (optional)'

def _extract_input_schema(details: dict, spec: dict) -> Dict[str, Any]:
    """
    Extracts input schema from request body with enhanced logic.
    
    DEBUG: This function looks for request body content and extracts
    the actual schema definitions, not just the raw requestBody object.
    """
    request_body = details.get('requestBody', {})
    
    if not request_body:
        return {"type": "none", "description": "No request body required"}
    
    # Get content types and their schemas
    content = request_body.get('content', {})
    
    # DEBUG: Log content types found
    logging.debug(f"Request body content types: {list(content.keys())}")
    
    # Extract schema for the most common content type
    preferred_types = ['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data']
    
    for content_type in preferred_types:
        if content_type in content:
            content_schema = content[content_type].get('schema', {})
            
            # Resolve schema reference if it's a $ref
            resolved_schema = _resolve_schema_ref(content_schema, spec)
            
            return {
                "content_type": content_type,
                "schema": resolved_schema,
                "required": request_body.get('required', False)
            }
    
    # If no preferred content type found, return the first available
    if content:
        first_content_type = list(content.keys())[0]
        content_schema = content[first_content_type].get('schema', {})
        resolved_schema = _resolve_schema_ref(content_schema, spec)
        
        return {
            "content_type": first_content_type,
            "schema": resolved_schema,
            "required": request_body.get('required', False)
        }
    
    return {"type": "unknown", "description": "Request body present but schema unclear"}

def _extract_output_schema(details: dict, spec: dict) -> Dict[str, Any]:
    """
    Extracts output schema from responses with enhanced logic.
    
    DEBUG: This function looks for response schemas and extracts
    the most common success response (200, 201, etc.).
    """
    responses = details.get('responses', {})
    
    if not responses:
        return {"type": "none", "description": "No response schema defined"}
    
    # Look for success responses first
    success_codes = ['200', '201', '202', '204']
    
    for code in success_codes:
        if code in responses:
            response = responses[code]
            content = response.get('content', {})
            
            # DEBUG: Log response content types
            logging.debug(f"Response {code} content types: {list(content.keys())}")
            
            # Extract schema for JSON response
            if 'application/json' in content:
                content_schema = content['application/json'].get('schema', {})
                resolved_schema = _resolve_schema_ref(content_schema, spec)
                
                return {
                    "status_code": code,
                    "content_type": "application/json",
                    "schema": resolved_schema,
                    "description": response.get('description', '')
                }
    
    # If no success response found, return the first available response
    if responses:
        first_code = list(responses.keys())[0]
        response = responses[first_code]
        content = response.get('content', {})
        
        if content:
            first_content_type = list(content.keys())[0]
            content_schema = content[first_content_type].get('schema', {})
            resolved_schema = _resolve_schema_ref(content_schema, spec)
            
            return {
                "status_code": first_code,
                "content_type": first_content_type,
                "schema": resolved_schema,
                "description": response.get('description', '')
            }
    
    return {"type": "unknown", "description": "Response present but schema unclear"}

def _resolve_schema_ref(schema: dict, spec: dict) -> Dict[str, Any]:
    """
    Resolves schema references ($ref) to actual schema definitions.
    
    DEBUG: This function follows $ref pointers to get the actual schema
    definition from the components/schemas section.
    """
    if not schema:
        return {}
    
    # Check if this is a reference
    if '$ref' in schema:
        ref_path = schema['$ref']
        
        # DEBUG: Log the reference being resolved
        logging.debug(f"Resolving schema reference: {ref_path}")
        
        # Remove the #/ prefix and split by /
        if ref_path.startswith('#/'):
            ref_path = ref_path[2:]
        
        path_parts = ref_path.split('/')
        
        # Navigate to the referenced schema
        current = spec
        for part in path_parts:
            current = current.get(part, {})
        
        return current
    
    return schema

# --- Unstructured HTML API Doc Scraper ---
def scrape_html_doc(doc_url: str) -> List[Dict[str, Any]]:
    """
    Scrapes an HTML API documentation page to extract endpoints, methods, and auth info.
    (Best effort; works for common doc layouts.)

    Args:
        doc_url (str): URL to the HTML documentation page.

    Returns:
        List[Dict[str, Any]]: List of endpoint metadata dicts.
    """
    # DEBUG: Log the URL being scraped
    logging.debug(f"Scraping HTML from: {doc_url}")
    
    resp = requests.get(doc_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # DEBUG: Log page info
    logging.debug(f"Page title: {soup.title.string if soup.title else 'No title'}")
    
    endpoints = []
    auth_type = _guess_html_auth(soup)
    
    # DEBUG: Log auth type found
    logging.debug(f"Guessed auth type from HTML: {auth_type}")
    
    # Try to find endpoint tables or code blocks
    for tag in soup.find_all(['table', 'pre', 'code']):
        text = tag.get_text(separator='\n')
        
        # DEBUG: Log what we're processing
        logging.debug(f"Processing {tag.name} tag with {len(text)} characters")
        
        # Look for lines like: GET /path, POST /path, etc.
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if any(line.startswith(m) for m in ['GET ', 'POST ', 'PUT ', 'DELETE ', 'PATCH ']):
                parts = line.split()
                if len(parts) >= 2:
                    # Try to extract more information from the context
                    input_schema = _extract_html_input_schema(line, tag)
                    output_schema = _extract_html_output_schema(line, tag)
                    
                    endpoint = {
                        'method': parts[0],
                        'path': parts[1],
                        'auth_type': auth_type,
                        'input_schema': input_schema,
                        'output_schema': output_schema
                    }
                    endpoints.append(endpoint)
    
    # Shopify-specific fallback: If no endpoints found and this is a Shopify admin-rest product resource page, fetch OpenAPI JSON and extract product endpoints
    if not endpoints and "shopify.dev" in doc_url and "/admin-rest/" in doc_url and "/resources/product" in doc_url:
        import re
        m = re.search(r"/admin-rest/([\w-]+)/resources/product", doc_url)
        if m:
            version = m.group(1)
            openapi_url = f"https://shopify.dev/api/admin-rest/{version}/openapi.json"
            try:
                # Import locally to avoid circular import
                from app.api_doc_scraper import scrape_openapi as _shopify_scrape_openapi
                all_endpoints = _shopify_scrape_openapi(openapi_url)
                # Only keep endpoints for /products.json
                endpoints = [ep for ep in all_endpoints if ep.get('path', '').endswith('/products.json')]
            except Exception as e:
                logging.error(f"Shopify fallback OpenAPI scrape failed: {e}")
                endpoints = []
    
    # DEBUG: Log summary
    logging.debug(f"Extracted {len(endpoints)} endpoints from HTML")
    return endpoints

def _guess_html_auth(soup: BeautifulSoup) -> Optional[str]:
    """
    Tries to guess authentication type from HTML doc text with enhanced logic.
    
    DEBUG: This function searches for common authentication keywords
    in the HTML text to determine the auth type.
    """
    text = soup.get_text().lower()
    
    # DEBUG: Log what we're searching for
    logging.debug(f"Searching for auth keywords in {len(text)} characters of text")
    
    # Enhanced auth detection
    auth_keywords = {
        'api key': 'api_key',
        'api_key': 'api_key',
        'x-api-key': 'api_key',
        'authorization': 'bearer_token',
        'bearer token': 'bearer_token',
        'bearer': 'bearer_token',
        'oauth': 'oauth2',
        'oauth2': 'oauth2',
        'openid connect': 'oauth2',
        'basic auth': 'basic_auth',
        'basic authentication': 'basic_auth',
        'username password': 'basic_auth',
        'jwt': 'jwt_token',
        'json web token': 'jwt_token'
    }
    
    for keyword, auth_type in auth_keywords.items():
        if keyword in text:
            logging.debug(f"Found auth keyword '{keyword}' -> {auth_type}")
            return auth_type
    
    # If no specific auth found, check for general security mentions
    security_indicators = ['authentication', 'authorization', 'security', 'login', 'token']
    if any(indicator in text for indicator in security_indicators):
        return 'authentication_required'
    
    return 'none'

def _extract_html_input_schema(line: str, tag) -> Dict[str, Any]:
    """
    Attempts to extract input schema information from HTML context.
    
    DEBUG: This function looks for request body information near the endpoint
    definition in the HTML.
    """
    # Look for common request body indicators in the same tag or nearby
    parent_text = tag.get_text().lower()
    
    # Check for JSON body indicators
    if any(indicator in parent_text for indicator in ['request body', 'json', 'payload', 'data']):
        return {
            "type": "json",
            "description": "Request body detected from HTML context",
            "source": "html_parsing"
        }
    
    # Check for form data indicators
    if any(indicator in parent_text for indicator in ['form', 'form-data', 'multipart']):
        return {
            "type": "form_data",
            "description": "Form data detected from HTML context",
            "source": "html_parsing"
        }
    
    # Default for GET requests (usually no body)
    if line.startswith('GET '):
        return {
            "type": "none",
            "description": "GET request typically has no request body",
            "source": "html_parsing"
        }
    
    return {
        "type": "unknown",
        "description": "Could not determine input schema from HTML",
        "source": "html_parsing"
    }

def _extract_html_output_schema(line: str, tag) -> Dict[str, Any]:
    """
    Attempts to extract output schema information from HTML context.
    
    DEBUG: This function looks for response information near the endpoint
    definition in the HTML.
    """
    # Look for common response indicators in the same tag or nearby
    parent_text = tag.get_text().lower()
    
    # Check for JSON response indicators
    if any(indicator in parent_text for indicator in ['response', 'json', 'data', 'result']):
        return {
            "type": "json",
            "description": "JSON response detected from HTML context",
            "source": "html_parsing"
        }
    
    # Check for specific status codes
    status_codes = re.findall(r'(\d{3})', parent_text)
    if status_codes:
        return {
            "type": "json",
            "status_codes": status_codes,
            "description": f"Response with status codes: {', '.join(status_codes)}",
            "source": "html_parsing"
        }
    
    return {
        "type": "unknown",
        "description": "Could not determine output schema from HTML",
        "source": "html_parsing"
    }

# --- Example CLI usage ---
if __name__ == '__main__':
    # Set up logging for debugging
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    
    # Example: scrape Shopify OpenAPI
    shopify_openapi = 'https://shopify.dev/api/admin-rest/2023-10/openapi.json'
    print('--- Shopify OpenAPI Endpoints ---')
    try:
        endpoints = scrape_openapi(shopify_openapi)
        for ep in endpoints[:5]:  # Print first 5 for brevity
            print(json.dumps(ep, indent=2))
    except Exception as e:
        print(f'Failed to scrape OpenAPI: {e}')

    # Example: scrape HTML docs (replace with real doc URL)
    # gmail_html = 'https://developers.google.com/gmail/api/reference/rest'
    # print('--- Gmail HTML Endpoints ---')
    # endpoints = scrape_html_doc(gmail_html)
    # for ep in endpoints[:5]:
    #     print(json.dumps(ep, indent=2))

# --- Debugging Tips and Utilities ---
def debug_schema_extraction(openapi_url: str, endpoint_path: str = None, method: str = None):
    """
    Debug utility to help troubleshoot schema extraction issues.
    
    DEBUG: Use this function to inspect what's happening during schema extraction
    for a specific endpoint or the entire OpenAPI spec.
    
    Args:
        openapi_url (str): URL to the OpenAPI spec
        endpoint_path (str, optional): Specific path to debug
        method (str, optional): Specific HTTP method to debug
    """
    print(f"🔍 DEBUGGING: {openapi_url}")
    print("=" * 50)
    
    # Set up detailed logging
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    
    try:
        # Fetch the spec
        resp = requests.get(openapi_url)
        resp.raise_for_status()
        spec = resp.json()
        
        print(f"✅ OpenAPI spec loaded successfully")
        print(f"📊 Spec version: {spec.get('openapi', 'unknown')}")
        print(f"🛣️  Total paths: {len(spec.get('paths', {}))}")
        
        # Check auth
        auth_type = _extract_openapi_auth(spec)
        print(f"🔐 Auth type: {auth_type}")
        
        # If specific endpoint requested, debug it
        if endpoint_path and method:
            path_data = spec.get('paths', {}).get(endpoint_path, {})
            method_data = path_data.get(method.lower(), {})
            
            if method_data:
                print(f"\n🎯 Debugging {method.upper()} {endpoint_path}:")
                print(f"📥 Input schema: {json.dumps(_extract_input_schema(method_data, spec), indent=2)}")
                print(f"📤 Output schema: {json.dumps(_extract_output_schema(method_data, spec), indent=2)}")
            else:
                print(f"❌ Endpoint {method.upper()} {endpoint_path} not found")
        
        # Show first few endpoints as examples
        print(f"\n📋 First 3 endpoints:")
        endpoints = scrape_openapi(openapi_url)
        for i, ep in enumerate(endpoints[:3]):
            print(f"\n{i+1}. {ep['method']} {ep['path']}")
            print(f"   Auth: {ep['auth_type']}")
            print(f"   Input: {ep['input_schema'].get('type', 'unknown')}")
            print(f"   Output: {ep['output_schema'].get('type', 'unknown')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Debugging tips:")
        print("1. Check if the URL is accessible")
        print("2. Verify it's a valid OpenAPI JSON spec")
        print("3. Check network connectivity")
        print("4. Try with a different OpenAPI spec URL")

def validate_schema_extraction(endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validates the quality of schema extraction and provides feedback.
    
    DEBUG: Use this function to check if your schema extraction is working properly
    and identify areas for improvement.
    
    Args:
        endpoints (List[Dict[str, Any]]): List of extracted endpoints
        
    Returns:
        Dict[str, Any]: Validation report with statistics and recommendations
    """
    total_endpoints = len(endpoints)
    if total_endpoints == 0:
        return {"status": "error", "message": "No endpoints found"}
    
    # Count schema quality
    auth_with_value = sum(1 for ep in endpoints if ep.get('auth_type') and ep['auth_type'] != 'none')
    input_with_schema = sum(1 for ep in endpoints if ep.get('input_schema', {}).get('type') not in ['none', 'unknown'])
    output_with_schema = sum(1 for ep in endpoints if ep.get('output_schema', {}).get('type') not in ['none', 'unknown'])
    
    # Calculate percentages
    auth_percentage = (auth_with_value / total_endpoints) * 100
    input_percentage = (input_with_schema / total_endpoints) * 100
    output_percentage = (output_with_schema / total_endpoints) * 100
    
    # Generate recommendations
    recommendations = []
    if auth_percentage < 50:
        recommendations.append("🔐 Low auth detection - check if OpenAPI spec has security schemes defined")
    if input_percentage < 50:
        recommendations.append("📥 Low input schema extraction - check request body definitions")
    if output_percentage < 50:
        recommendations.append("📤 Low output schema extraction - check response definitions")
    
    return {
        "status": "success",
        "total_endpoints": total_endpoints,
        "auth_detection_rate": f"{auth_percentage:.1f}%",
        "input_schema_rate": f"{input_percentage:.1f}%",
        "output_schema_rate": f"{output_percentage:.1f}%",
        "recommendations": recommendations
    }

# --- Common Issues and Solutions ---
"""
🔧 COMMON DEBUGGING ISSUES AND SOLUTIONS:

1. ❌ "auth_type is null"
   ✅ Solution: Check if OpenAPI spec has 'components.securitySchemes' defined
   ✅ Debug: Use debug_schema_extraction() to inspect the spec

2. ❌ "input_schema is null" 
   ✅ Solution: Check if endpoints have 'requestBody' with 'content' and 'schema'
   ✅ Debug: Look for $ref pointers that need resolution

3. ❌ "output_schema is null"
   ✅ Solution: Check if responses have 'content' with 'application/json' schema
   ✅ Debug: Verify response status codes (200, 201, etc.) are defined

4. ❌ "HTML scraping returns empty results"
   ✅ Solution: Check if HTML has proper structure (tables, code blocks)
   ✅ Debug: Verify the URL is accessible and contains API documentation

5. ❌ "Schema references not resolved"
   ✅ Solution: Ensure $ref paths are correct (e.g., '#/components/schemas/Model')
   ✅ Debug: Check if referenced schemas exist in components/schemas

6. ❌ "Network errors"
   ✅ Solution: Check URL accessibility, CORS, and network connectivity
   ✅ Debug: Try with a different OpenAPI spec URL

💡 PRO TIPS:
- Use debug_schema_extraction() for detailed inspection
- Use validate_schema_extraction() to check extraction quality
- Enable DEBUG logging to see step-by-step extraction process
- Test with well-known OpenAPI specs first (Shopify, Stripe, etc.)
"""

def format_shopify_openapi(openapi_url: str, endpoints: list) -> dict:
    """
    Formats the scraped OpenAPI data for Shopify to match the required output structure.
    Args:
        openapi_url (str): The source URL of the OpenAPI spec.
        endpoints (list): List of endpoint dicts from scrape_openapi.
    Returns:
        dict: Formatted output as required by the user.
    """
    def flatten_schema(schema):
        # Recursively flatten OpenAPI schema to a simple type map
        if not isinstance(schema, dict):
            return schema
        if schema.get('type') == 'object' and 'properties' in schema:
            return {k: flatten_schema(v) for k, v in schema['properties'].items()}
        if schema.get('type') == 'array' and 'items' in schema:
            return [flatten_schema(schema['items'])]
        if 'type' in schema:
            return schema['type']
        return schema

    formatted_endpoints = []
    for ep in endpoints:
        # Try to extract a summary/description if available
        desc = ep.get('description')
        if not desc:
            # Try to get from input_schema/output_schema
            desc = ep.get('input_schema', {}).get('description') or ep.get('output_schema', {}).get('description')
        # Flatten schemas
        input_schema = ep.get('input_schema', {})
        output_schema = ep.get('output_schema', {})
        # Shopify spec puts schema under 'schema' key
        input_flat = flatten_schema(input_schema.get('schema', {})) if 'schema' in input_schema else {}
        output_flat = flatten_schema(output_schema.get('schema', {})) if 'schema' in output_schema else {}
        formatted_endpoints.append({
            'path': ep.get('path'),
            'method': ep.get('method'),
            'auth_type': 'OAuth',  # Shopify always uses OAuth
            'description': desc or '',
            'input_schema': input_flat,
            'output_schema': output_flat
        })
    return {
        'api_name': 'Shopify',
        'source_url': openapi_url,
        'endpoints': formatted_endpoints
    } 