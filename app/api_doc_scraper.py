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
"""

import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import json

# --- Structured API (OpenAPI/Swagger) Scraper ---
def scrape_openapi(openapi_url: str) -> List[Dict[str, Any]]:
    """
    Fetches and parses an OpenAPI/Swagger JSON spec to extract endpoints, methods, auth, and schemas.

    Args:
        openapi_url (str): URL to the OpenAPI/Swagger JSON.

    Returns:
        List[Dict[str, Any]]: List of endpoint metadata dicts.
    """
    resp = requests.get(openapi_url)
    resp.raise_for_status()
    spec = resp.json()
    endpoints = []
    auth_type = _extract_openapi_auth(spec)
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            endpoint = {
                'method': method.upper(),
                'path': path,
                'auth_type': auth_type,
                'input_schema': details.get('requestBody', {}),
                'output_schema': details.get('responses', {})
            }
            endpoints.append(endpoint)
    return endpoints

def _extract_openapi_auth(spec: dict) -> Optional[str]:
    """
    Extracts authentication type from OpenAPI spec.
    """
    security = spec.get('security', [])
    components = spec.get('components', {})
    security_schemes = components.get('securitySchemes', {})
    if not security_schemes:
        return None
    auth_types = ', '.join([scheme.get('type', 'unknown') for scheme in security_schemes.values()])
    if security:
        return auth_types or 'required'
    else:
        return auth_types + ' (optional)'

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
    resp = requests.get(doc_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    endpoints = []
    # Try to find endpoint tables or code blocks
    for tag in soup.find_all(['table', 'pre', 'code']):
        text = tag.get_text(separator='\n')
        # Look for lines like: GET /path, POST /path, etc.
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if any(line.startswith(m) for m in ['GET ', 'POST ', 'PUT ', 'DELETE ', 'PATCH ']):
                parts = line.split()
                if len(parts) >= 2:
                    endpoints.append({
                        'method': parts[0],
                        'path': parts[1],
                        'auth_type': _guess_html_auth(soup),
                        'input_schema': None,
                        'output_schema': None
                    })
    return endpoints

def _guess_html_auth(soup: BeautifulSoup) -> Optional[str]:
    """
    Tries to guess authentication type from HTML doc text.
    """
    text = soup.get_text().lower()
    if 'api key' in text:
        return 'apiKey'
    if 'oauth' in text:
        return 'oauth2'
    if 'bearer token' in text:
        return 'bearer'
    if 'basic auth' in text:
        return 'basic'
    return None

# --- Example CLI usage ---
if __name__ == '__main__':
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