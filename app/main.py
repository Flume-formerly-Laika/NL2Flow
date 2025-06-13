"""
@file main.py
@brief Main application entry point
@author Huy Le (huyisme-005)
"""

# import fastapi for creating the API, request handling, and HTTP exceptions
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse

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

app = FastAPI(
    title="NL2Flow API",
    description="Natural Language to Automation Flow Generator",
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