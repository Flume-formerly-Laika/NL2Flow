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

app = FastAPI(
    title="NL2Flow API",
    description="Natural Language to Automation Flow Generator with API Documentation Scraper",
    version="1.0.0"
) # main FastAPI application instance

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
                        "openapi_url": "https://shopify.dev/api/admin-rest/2023-10/openapi.json"
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
                    http://localhost:8000/scrape-openapi?openapi_url=https://shopify.dev/api/admin-rest/2023-10/openapi.json
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
async def scrape_openapi_endpoint(request: Request):
    """
    Scrape OpenAPI/Swagger documentation from a URL
    
    Debugging tips:
    - Ensure the openapi_url is a direct link to a JSON spec (not an HTML doc page).
    - For Shopify, the correct format is https://shopify.dev/api/admin-rest/<version>/openapi.json
    - If you get a 404 error, check if the URL contains /docs/ instead of /api/ and auto-correct it.
    - If you get a JSON decode error, the URL is likely not a JSON file.
    - If you get repeated errors, try using the 'latest' version: https://shopify.dev/api/admin-rest/latest/openapi.json
    - Use /scrape-html for HTML documentation pages.
    """
    try:
        body = await request.json()
        openapi_url = body.get("openapi_url")
        if not openapi_url:
            raise HTTPException(status_code=400, detail="openapi_url is required")
        # Shopify auto-correction: convert /docs/ to /api/ if needed
        if "shopify.dev" in openapi_url and "/docs/" in openapi_url:
            openapi_url = openapi_url.replace("/docs/", "/api/")
            # If the URL ends with /resources/product, replace with /openapi.json
            if openapi_url.endswith("/resources/product"):
                openapi_url = openapi_url.replace("/resources/product", "/openapi.json")
        # If the user gives a versioned docs page, try to convert to openapi.json
        if "shopify.dev" in openapi_url and openapi_url.endswith("/openapi.json") and "/docs/" in openapi_url:
            openapi_url = openapi_url.replace("/docs/", "/api/")
        logging.debug(f"Scraping OpenAPI from: {openapi_url}")
        trace_id = log_request(request, f"Scraping OpenAPI: {openapi_url}")
        try:
            endpoints = scrape_openapi(openapi_url)
        except requests.exceptions.HTTPError as e:
            # If 404 and Shopify, try 'latest' OpenAPI JSON
            if ("shopify.dev" in openapi_url and e.response is not None and e.response.status_code == 404):
                logging.warning(f"404 for {openapi_url}, trying latest OpenAPI JSON")
                openapi_url = "https://shopify.dev/api/admin-rest/latest/openapi.json"
                endpoints = scrape_openapi(openapi_url)
            else:
                raise
        except json.JSONDecodeError as e:
            # If JSON decode error, likely HTML page, try 'latest' OpenAPI JSON for Shopify
            if "shopify.dev" in openapi_url:
                logging.warning(f"JSON decode error for {openapi_url}, trying latest OpenAPI JSON")
                openapi_url = "https://shopify.dev/api/admin-rest/latest/openapi.json"
                endpoints = scrape_openapi(openapi_url)
            else:
                raise
        validation = validate_schema_extraction(endpoints)
        # Shopify-specific formatting
        if "shopify.dev" in openapi_url:
            result = format_shopify_openapi(openapi_url, endpoints)
            result["trace_id"] = trace_id
            return result
        # Default output for other APIs
        return {
            "trace_id": trace_id,
            "openapi_url": openapi_url,
            "endpoints_count": len(endpoints),
            "extraction_quality": validation,
            "endpoints": endpoints
        }
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
async def scrape_openapi_get(openapi_url: str = "https://shopify.dev/api/admin-rest/2023-10/openapi.json"):
    """
    Browser-friendly OpenAPI scraper with default example
    
    DEBUG: This endpoint provides a simple way to test OpenAPI scraping in the browser.
    The default URL is Shopify's OpenAPI spec which is well-structured and public.
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