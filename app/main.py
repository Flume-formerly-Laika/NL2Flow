"""
@file main.py
@brief Main application entry point
@author Huy Le (huyisme-005)
"""

# import fastapi for creating the API, request handling, and HTTP exceptions
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import os
import logging
import json
import requests
from pydantic import BaseModel
import datetime
from typing import Dict, Any

# import models for request payload
from app.models import NLRequest

# import gpt handler for extracting intent
from app.gpt_handler import extract_intent

# import transformer for building flow JSON and utils for logging and validation
from app.transformer import build_flow_json

# import logger for logging requests
from app.utils.logger import log_request

# import validator for validating the flow against JSON schema
from app.utils.validator import validate_flow

# import API doc scraper
from app.api_doc_scraper import scrape_openapi, scrape_html_doc, validate_schema_extraction, format_shopify_openapi

# import DynamoDB utility
from app.utils.dynamodb_snapshots import store_schema_snapshot, get_schema_by_version

# import schema diff engine
from app.utils.schema_diff import diff_schema_versions

app = FastAPI(
    title="NL2Flow API",
    description="Natural Language to Automation Flow Generator with API Documentation Scraper",
    version="1.0.0"
) # main FastAPI application instance

class OpenAPIRequest(BaseModel):
    openapi_url: str

class DiffRequest(BaseModel):
    old_schema: Dict[str, Any]
    new_schema: Dict[str, Any]

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic information and links"""
    return """
    <html>
        <head>
            <title>NL2Flow API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #333; text-align: center; }
                .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
                .method { color: #007bff; font-weight: bold; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .example { background: #e9ecef; padding: 10px; margin: 10px 0; border-radius: 3px; font-family: monospace; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔄 NL2Flow API</h1>
                <p>Welcome to the Natural Language to Automation Flow Generator API!</p>
                
                <h2>Available Endpoints:</h2>
                
                <div class="endpoint">
                    <p><span class="method">GET</span> <strong>/health</strong> - Health check endpoint</p>
                </div>
                
                <div class="endpoint">
                    <p><span class="method">POST</span> <strong>/parse-request</strong> - Convert natural language to automation flow</p>
                    <div class="example">
                    {
                        "user_input": "When a new user signs up, send a welcome email with their name and signup date."
                    }
                    </div>
                </div>

                <div class="endpoint">
                    <p><span class="method">GET</span> <strong>/parse-request</strong> - Browser-friendly version for testing</p>
                    <p><a href="/parse-request">Try with default example</a></p>
                    <div class="example">
                    http://localhost:8000/parse-request?user_input=Your request here
                    </div>
                </div>

                <div class="endpoint">
                    <p><span class="method">POST</span> <strong>/scrape-openapi</strong> - Scrape OpenAPI/Swagger documentation</p>
                    <div class="example">
                    {
                        "openapi_url": "https://petstore.swagger.io/v2/swagger.json"
                    }
                    </div>
                </div>

                <div class="endpoint">
                    <p><span class="method">POST</span> <strong>/scrape-html</strong> - Scrape HTML API documentation</p>
                    <div class="example">
                    {
                        "doc_url": "https://developers.google.com/gmail/api/reference/rest"
                    }
                    </div>
                </div>

                <div class="endpoint">
                    <p><span class="method">GET</span> <strong>/scrape-openapi</strong> - Browser-friendly OpenAPI scraper</p>
                    <p><a href="/scrape-openapi">Try with default example</a></p>
                    <div class="example">
                    http://localhost:8000/scrape-openapi?openapi_url=https://petstore.swagger.io/v2/swagger.json
                    </div>
                </div>

                <div class="endpoint">
                    <p><span class="method">GET</span> <strong>/scrape-html</strong> - Browser-friendly HTML scraper</p>
                    <p><a href="/scrape-html">Try with default example</a></p>
                    <div class="example">
                    http://localhost:8000/scrape-html?doc_url=https://developers.google.com/gmail/api/reference/rest
                    </div>
                </div>
                
                <h2>Documentation:</h2>
                <p>📚 <a href="/docs">Interactive API Documentation (Swagger UI)</a></p>
                <p>📋 <a href="/redoc">Alternative Documentation (ReDoc)</a></p>
                
                <h2>Quick Test:</h2>
                <p>Try the health check: <a href="/health">/health</a></p>
                
                <h2>Example Usage:</h2>
                <div class="example">
curl -X POST "http://localhost:8000/parse-request" \
     -H "Content-Type: application/json" \
     -d '{"user_input": "When a new user signs up, send a welcome email"}'
                </div>

                <h2>Diff Engine</h2>
                <p>Compare two schema versions and get a structured diff of changes:</p>
                <div class="example">
from app.utils.schema_diff import diff_schema_versions

old_schema = {
    "product": {
        "title": "string",
        "vendor": "string"
    }
}

new_schema = {
    "product": {
        "title": "string",
        "vendor": "string",
        "tags": "string"
    }
}

diff = diff_schema_versions(old_schema, new_schema)
# Returns a list of changes (additions, removals, modifications)
                </div>
                <p><strong>Example Output:</strong></p>
                <div class="example">
[
  {"op": "add", "path": "product/tags", "old": null, "new": "string"}
]
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "NL2Flow API is running"}

@app.post("/parse-request") # Add a path operation using an HTTP POST operation.
async def parse_request(payload: NLRequest, request: Request):
    '''
    @brief Parses the natural language request 'n' returns the corresponding email flow JSON
    @param payload the request payload containing user input
    @param request the FastAPI request object
    @return a JSON response containing the trace ID and the email flow JSON
    @raises HTTPException if processing fails
    '''
    trace_id = log_request(request, payload.user_input)
    
    try:
        intent = await extract_intent(payload.user_input)
        flow_json = build_flow_json(intent)
        validate_flow(flow_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    return {"trace_id": trace_id, "flow": flow_json}

@app.get("/parse-request")
async def parse_request_get(user_input: str = "When a new user signs up, send a welcome email"):
    """
    GET version of parse-request for easy browser testing
    Example: http://localhost:8000/parse-request?user_input=Your request here
    """
    # Create a mock request object for logging
    class MockRequest:
        def __init__(self):
            self.url = type('obj', (object,), {'path': '/parse-request'})
    
    mock_request = MockRequest()
    payload = NLRequest(user_input=user_input)
    
    trace_id = log_request(mock_request, payload.user_input)
    
    try:
        intent = await extract_intent(payload.user_input)
        flow_json = build_flow_json(intent)
        validate_flow(flow_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    return {"trace_id": trace_id, "flow": flow_json}

@app.post("/scrape-openapi")
async def scrape_openapi_endpoint(payload: OpenAPIRequest, request: Request):
    """
    Scrape OpenAPI/Swagger documentation from a URL
    
    Debugging tips:
    - Ensure the openapi_url is a direct link to a JSON spec (not an HTML doc page).
    - Example: https://petstore.swagger.io/v2/swagger.json
    - If you get a 404 error, check if the URL is correct and accessible.
    - If you get a JSON decode error, the URL is likely not a JSON file.
    - Use /scrape-html for HTML documentation pages.
    """
    try:
        openapi_url = payload.openapi_url
        if not openapi_url:
            raise HTTPException(status_code=400, detail="openapi_url is required")
        logging.debug(f"Scraping OpenAPI from: {openapi_url}")
        trace_id = log_request(request, f"Scraping OpenAPI: {openapi_url}")
        api_name = None
        try:
            endpoints = scrape_openapi(openapi_url)
            # Try to fetch the API name from the OpenAPI spec
            # Fetch the spec directly to get info.title
            spec_resp = requests.get(openapi_url)
            spec_resp.raise_for_status()
            spec = spec_resp.json()
            api_name = spec.get("info", {}).get("title") or "UnknownAPI"
        except requests.exceptions.HTTPError as e:
            api_name = "UnknownAPI"
            raise
        except json.JSONDecodeError as e:
            api_name = "UnknownAPI"
            raise
        except Exception as e:
            api_name = "UnknownAPI"
            raise
        validation = validate_schema_extraction(endpoints)
        # Store each endpoint as a snapshot in DynamoDB
        now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        now_iso = now.isoformat().replace('+00:00', 'Z')
        now_ts = int(now.timestamp())
        stored_snapshots = []
        for ep in endpoints:
            schema_json = {
                "input": ep.get("input_schema", {}),
                "output": ep.get("output_schema", {})
            }
            snapshot = store_schema_snapshot(
                api_name=api_name,
                endpoint=ep.get("path"),
                method=ep.get("method"),
                schema=schema_json,
                metadata={
                    "auth_type": ep.get("auth_type"),
                    "source_url": openapi_url,
                    "version_ts": now_iso
                },
                timestamp=now_ts
            )
            stored_snapshots.append(snapshot)
        # Format output for the first endpoint as an example (can be extended for all)
        if endpoints:
            ep = endpoints[0]
            schema_json = {
                "input": ep.get("input_schema", {}),
                "output": ep.get("output_schema", {})
            }
            result = {
                "trace_id": trace_id,
                "api_name": api_name,
                "version_ts": now_iso,
                "endpoint": ep.get("path"),
                "method": ep.get("method"),
                "auth_type": ep.get("auth_type"),
                "schema_json": schema_json,
                "source_url": openapi_url,
                "extraction_quality": validation
            }
            return result
        return {"message": "No endpoints found in OpenAPI spec."}
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error scraping OpenAPI: {e}")
        raise HTTPException(status_code=400, detail=f"Network error: {str(e)}.\n\nDebugging tips: Make sure the URL is accessible and is a direct OpenAPI JSON file. For Shopify, try using https://shopify.dev/api/admin-rest/latest/openapi.json.")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in OpenAPI spec: {e}")
        raise HTTPException(status_code=400, detail="Invalid OpenAPI JSON specification.\n\nDebugging tips: The URL you provided is likely an HTML page, not a JSON file. For Shopify, use https://shopify.dev/api/admin-rest/latest/openapi.json.")
    except Exception as e:
        logging.error(f"OpenAPI scraping failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}.\n\nDebugging tips: If this is a Shopify URL, try using https://shopify.dev/api/admin-rest/latest/openapi.json. If the error persists, check your network connection and the URL's accessibility.")

@app.get("/scrape-openapi")
async def scrape_openapi_get(openapi_url: str = "https://petstore.swagger.io/v2/swagger.json"):
    """
    Browser-friendly OpenAPI scraper with default example
    
    DEBUG: This endpoint provides a simple way to test OpenAPI scraping in the browser.
    The default URL is Swagger Petstore's OpenAPI spec which is well-structured and public.
    """
    try:
        # DEBUG: Log the request
        logging.debug(f"GET request scraping OpenAPI from: {openapi_url}")
        
        endpoints = scrape_openapi(openapi_url)
        
        # Validate extraction quality
        validation = validate_schema_extraction(endpoints)
        
        return {
            "openapi_url": openapi_url,
            "endpoints_count": len(endpoints),
            "extraction_quality": validation,
            "endpoints": endpoints[:10],  # Show first 10 for browser display
            "debug_tip": "Use POST /scrape-openapi for full results or debug_schema_extraction() for detailed analysis"
        }
    except Exception as e:
        logging.error(f"OpenAPI scraping failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.post("/scrape-html")
async def scrape_html_endpoint(request: Request):
    """
    Scrape HTML API documentation from a URL
    
    DEBUG: This endpoint extracts endpoints from HTML documentation pages.
    Common issues: No structured data, missing tables/code blocks, JavaScript-rendered content.
    """
    try:
        body = await request.json()
        doc_url = body.get("doc_url")
        if not doc_url:
            raise HTTPException(status_code=400, detail="doc_url is required")
        
        # DEBUG: Log the request
        logging.debug(f"Scraping HTML from: {doc_url}")
        
        trace_id = log_request(request, f"Scraping HTML: {doc_url}")
        endpoints = scrape_html_doc(doc_url)
        
        # Validate extraction quality
        validation = validate_schema_extraction(endpoints)
        
        return {
            "trace_id": trace_id,
            "doc_url": doc_url,
            "endpoints_count": len(endpoints),
            "extraction_quality": validation,
            "endpoints": endpoints
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error scraping HTML: {e}")
        raise HTTPException(status_code=400, detail=f"Network error: {str(e)}")
    except Exception as e:
        logging.error(f"HTML scraping failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/scrape-html")
async def scrape_html_get(doc_url: str = "https://developers.google.com/gmail/api/reference/rest"):
    """
    Browser-friendly HTML scraper with default example
    
    DEBUG: This endpoint provides a simple way to test HTML scraping in the browser.
    The default URL is Gmail's API reference which has structured documentation.
    """
    try:
        # DEBUG: Log the request
        logging.debug(f"GET request scraping HTML from: {doc_url}")
        
        endpoints = scrape_html_doc(doc_url)
        
        # Validate extraction quality
        validation = validate_schema_extraction(endpoints)
        
        # Shopify-specific formatting for HTML scraping (force for product resource URLs)
        if "shopify.dev" in doc_url and "/admin-rest/" in doc_url and "/resources/product" in doc_url:
            import re
            m = re.search(r"/admin-rest/([\w-]+)/resources/product", doc_url)
            version = m.group(1) if m else None
            # Patch endpoint paths to use the version from the doc_url
            patched_endpoints = []
            for ep in endpoints:
                patched_ep = ep.copy()
                if version and '/products.json' in ep.get('path', ''):
                    patched_ep['path'] = f"/admin/api/{version}/products.json"
                patched_endpoints.append(patched_ep)
            # If no endpoints, create a default structure (optional, for robustness)
            result = format_shopify_openapi(doc_url, patched_endpoints)
            result["source_url"] = doc_url
            result["doc_url"] = doc_url
            result["endpoints_count"] = len(patched_endpoints)
            result["extraction_quality"] = validation
            result["debug_tip"] = "HTML scraping is best-effort. For better results, use OpenAPI specs when available."
            return result
        
        return {
            "doc_url": doc_url,
            "endpoints_count": len(endpoints),
            "extraction_quality": validation,
            "endpoints": endpoints[:10],  # Show first 10 for browser display
            "debug_tip": "HTML scraping is best-effort. For better results, use OpenAPI specs when available."
        }
    except Exception as e:
        logging.error(f"HTML scraping failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(os.path.dirname(__file__), "static", "favicon.ico")
    return FileResponse(favicon_path)

# New endpoint to retrieve a schema snapshot by API name and timestamp
@app.get("/schema-snapshot")
async def get_schema_snapshot(api_name: str, timestamp: int):
    item = get_schema_by_version(api_name, timestamp)
    if not item:
        raise HTTPException(status_code=404, detail="Schema snapshot not found.")
    # Format output to match the required format
    return {
        "api_name": item["api_name"],
        "version_ts": datetime.datetime.fromtimestamp(int(item["timestamp"]), datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        "endpoint": item["endpoint"],
        "method": item["method"],
        "auth_type": item.get("metadata", {}).get("auth_type"),
        "schema_json": item["schema"],
        "source_url": item.get("metadata", {}).get("source_url")
    }

@app.post("/diff-schemas", tags=["Diff Engine"])
async def diff_schemas_endpoint(payload: DiffRequest):
    """
    Diff Engine: Compare two schema versions and return a structured diff.
    - **old_schema**: The original schema (JSON object)
    - **new_schema**: The new schema (JSON object)
    Returns a list of changes (additions, removals, modifications).

    **Diff result explanation:**
    Each item in the result list is a change operation with:
    - `op`: The operation type. One of:
        - `add`: This field/path was added in the new schema.
        - `remove`: This field/path was removed from the old schema.
        - `change`: The value/type at this path changed between old and new.
    - `path`: The JSON path to the field that changed (e.g., 'product/tags').
    - `old`: The value/type in the old schema (or None if added).
    - `new`: The value/type in the new schema (or None if removed).
    """
    diff = diff_schema_versions(payload.old_schema, payload.new_schema)

    # Analyze the diff result
    added = [d for d in diff if d['op'] == 'add']
    removed = [d for d in diff if d['op'] == 'remove']
    changed = [d for d in diff if d['op'] == 'change']

    explanation_lines = []
    if not diff:
        explanation_lines.append("No differences found between the two schemas.")
    else:
        if added:
            explanation_lines.append(f"{len(added)} field(s) added: " + ", ".join(d['path'] for d in added))
        if removed:
            explanation_lines.append(f"{len(removed)} field(s) removed: " + ", ".join(d['path'] for d in removed))
        if changed:
            explanation_lines.append(f"{len(changed)} field(s) changed: " + ", ".join(d['path'] for d in changed))
        explanation_lines.append(
            "Each item in the result is a change operation with:\n"
            "- op: The operation type (add, remove, change).\n"
            "- path: The JSON path to the field that changed.\n"
            "- old: The value/type in the old schema (or None if added).\n"
            "- new: The value/type in the new schema (or None if removed)."
        )

    explanation = "\n".join(explanation_lines)
    # Replace newlines with <br> for better display in Swagger UI and browsers
    explanation_html = explanation.replace("\n", "<br>")
    return {"diff": diff, "explanation": explanation_html}