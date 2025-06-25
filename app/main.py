"""
@file main.py
@brief Main application entry point
@author Huy Le (huyisme-005)
"""

# import fastapi for creating the API, request handling, and HTTP exceptions
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import os

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
from app.api_doc_scraper import scrape_openapi, scrape_html_doc

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
    """
    try:
        body = await request.json()
        openapi_url = body.get("openapi_url")
        if not openapi_url:
            raise HTTPException(status_code=400, detail="openapi_url is required")
        
        trace_id = log_request(request, f"Scraping OpenAPI: {openapi_url}")
        endpoints = scrape_openapi(openapi_url)
        
        return {
            "trace_id": trace_id,
            "openapi_url": openapi_url,
            "endpoints_count": len(endpoints),
            "endpoints": endpoints
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/scrape-openapi")
async def scrape_openapi_get(openapi_url: str = "https://shopify.dev/api/admin-rest/2023-10/openapi.json"):
    """
    GET version of scrape-openapi for easy browser testing
    """
    class MockRequest:
        def __init__(self):
            self.url = type('obj', (object,), {'path': '/scrape-openapi'})
    
    mock_request = MockRequest()
    trace_id = log_request(mock_request, f"Scraping OpenAPI: {openapi_url}")
    
    try:
        endpoints = scrape_openapi(openapi_url)
        return {
            "trace_id": trace_id,
            "openapi_url": openapi_url,
            "endpoints_count": len(endpoints),
            "endpoints": endpoints[:10]  # Show first 10 endpoints for browser display
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.post("/scrape-html")
async def scrape_html_endpoint(request: Request):
    """
    Scrape HTML API documentation from a URL
    """
    try:
        body = await request.json()
        doc_url = body.get("doc_url")
        if not doc_url:
            raise HTTPException(status_code=400, detail="doc_url is required")
        
        trace_id = log_request(request, f"Scraping HTML: {doc_url}")
        endpoints = scrape_html_doc(doc_url)
        
        return {
            "trace_id": trace_id,
            "doc_url": doc_url,
            "endpoints_count": len(endpoints),
            "endpoints": endpoints
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/scrape-html")
async def scrape_html_get(doc_url: str = "https://developers.google.com/gmail/api/reference/rest"):
    """
    GET version of scrape-html for easy browser testing
    """
    class MockRequest:
        def __init__(self):
            self.url = type('obj', (object,), {'path': '/scrape-html'})
    
    mock_request = MockRequest()
    trace_id = log_request(mock_request, f"Scraping HTML: {doc_url}")
    
    try:
        endpoints = scrape_html_doc(doc_url)
        return {
            "trace_id": trace_id,
            "doc_url": doc_url,
            "endpoints_count": len(endpoints),
            "endpoints": endpoints[:10]  # Show first 10 endpoints for browser display
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(os.path.dirname(__file__), "static", "favicon.ico")
    return FileResponse(favicon_path)