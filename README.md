# NL2Flow: Natural Language to Automation Flow Generator

This project converts natural language automation requests into structured flow definitions using Google Gemini, FastAPI, and simplified field mapping. It also includes API documentation scraping, schema versioning, and schema diff capabilities.

## Features
- Natural language input via REST API
- Google Gemini intent extraction
- Field mapping via dictionary rules
- Validated JSON flow output
- **API Documentation Scraping** - Extract endpoints from OpenAPI specs and HTML docs
- **Schema Versioning** - Store and retrieve API schemas with DynamoDB
- **Schema Diff Engine** - Compare schema versions to monitor changes
- Cross-platform support (Windows PowerShell, Command Prompt, Unix/Linux)

## Quick Setup

### For Windows PowerShell Users:
```powershell
# Run the setup script
.\setup.ps1

# Edit the .env file to add your Google API key
notepad .env

# Start the application
.\run.ps1
```

### For Windows Command Prompt Users:
```cmd
# Install dependencies
pip install -r requirements.txt

# Copy and edit .env file
copy .env.example .env
notepad .env

# Start the application
run.bat
```

### For Unix/Linux/macOS Users:
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and edit .env file
cp .env.example .env
nano .env

# Make script executable and run
chmod +x run.sh
./run.sh
```

## Configuration

1. **Get a Google API key** from https://makersuite.google.com/app/apikey
2. **Edit the `.env` file** and replace `your_google_api_key_here` with your actual API key:
   ```
   GOOGLE_API_KEY=sk-your-actual-api-key-here
   ```
3. **Optional: Configure DynamoDB** (for schema versioning):
   ```
   DYNAMODB_SCHEMA_TABLE=The name you want to give the table
   ```

## API Documentation

The server runs on `http://localhost:8000`

### Available Endpoints

#### 1. Health Check
- **URL**: `GET /health`
- **Purpose**: Check if the API is running
- **Response**: 
  ```json
  {
    "status": "ok",
    "message": "NL2Flow API is running"
  }
  ```

#### 2. Parse Natural Language Request (POST)
- **URL**: `POST /parse-request`
- **Purpose**: Convert natural language to automation flow
- **Content-Type**: `application/json`

#### 3. Parse Natural Language Request (GET)
- **URL**: `GET /parse-request`
- **Purpose**: Browser-friendly version for testing
- **Query Parameter**: `user_input` (optional, defaults to example)

#### 4. Scrape OpenAPI Documentation (POST)
- **URL**: `POST /scrape-openapi`
- **Purpose**: Extract endpoints from OpenAPI/Swagger JSON specs
- **Content-Type**: `application/json`
- **Body**: `{"openapi_url": "https://api.example.com/openapi.json"}`

#### 5. Scrape OpenAPI Documentation (GET)
- **URL**: `GET /scrape-openapi`
- **Purpose**: Browser-friendly OpenAPI scraper
- **Query Parameter**: `openapi_url` (optional, defaults to Shopify API)

#### 6. Scrape HTML Documentation (POST)
- **URL**: `POST /scrape-html`
- **Purpose**: Extract endpoints from HTML documentation pages
- **Content-Type**: `application/json`
- **Body**: `{"doc_url": "https://docs.example.com/api"}`

#### 7. Scrape HTML Documentation (GET)
- **URL**: `GET /scrape-html`
- **Purpose**: Browser-friendly HTML scraper
- **Query Parameter**: `doc_url` (optional, defaults to Gmail API docs)

#### 8. Get Schema Snapshot
- **URL**: `GET /schema-snapshot`
- **Purpose**: Retrieve a specific schema version by API name and timestamp
- **Query Parameters**: `api_name`, `timestamp`

#### 9. Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Usage Guide

### Request Format

#### POST Request
```bash
POST http://localhost:8000/parse-request
Content-Type: application/json

{
  "user_input": "Your natural language automation request here"
}
```

#### GET Request (for browser testing)
```
http://localhost:8000/parse-request?user_input=Your request here
```

### Request Payload

The request payload must contain a `user_input` field with your natural language description:

```json
{
  "user_input": "string (required, minimum 1 character)"
}
```

**Requirements:**
- `user_input` must be a non-empty string
- Describe the automation you want in plain English
- Include trigger events and desired actions

### Response Format

All successful responses return the following structure:

```json
{
  "trace_id": "unique-uuid-for-tracking",
  "flow": {
    "flow": {
      "trigger": {
        "event": "trigger_type"
      },
      "actions": [
        {
          "action_type": "send_email",
          "template_id": "template_name",
          "params": {
            "field_name": "{{ user.source.field }}"
          }
        }
      ]
    }
  }
}
```

### Examples

#### Example 1: Welcome Email
**Request:**
```bash
curl -X POST "http://localhost:8000/parse-request" \
     -H "Content-Type: application/json" \
     -d '{
       "user_input": "When a new user signs up, send a welcome email with their name and signup date."
     }'
```

**Response:**
```json
{
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "flow": {
    "flow": {
      "trigger": {
        "event": "user_signup"
      },
      "actions": [
        {
          "action_type": "send_email",
          "template_id": "welcome",
          "params": {
            "first_name": "{{ user.user.name }}",
            "user_email": "{{ user.user.email }}",
            "registration_date": "{{ user.user.signup_date }}"
          }
        }
      ]
    }
  }
}
```

#### Example 2: Order Confirmation
**Request:**
```json
{
  "user_input": "After a customer places an order, send them a confirmation email with order details"
}
```

**Response:**
```json
{
  "trace_id": "550e8400-e29b-41d4-a716-446655440001",
  "flow": {
    "flow": {
      "trigger": {
        "event": "order_placed"
      },
      "actions": [
        {
          "action_type": "send_email",
          "template_id": "confirmation",
          "params": {
            "first_name": "{{ user.user.name }}",
            "user_email": "{{ user.user.email }}"
          }
        }
      ]
    }
  }
}
```

#### Example 3: Reminder Email
**Request:**
```json
{
  "user_input": "Send a reminder email to users who haven't completed their profile"
}
```

**Response:**
```json
{
  "trace_id": "550e8400-e29b-41d4-a716-446655440002",
  "flow": {
    "flow": {
      "trigger": {
        "event": "user_signup"
      },
      "actions": [
        {
          "action_type": "send_email",
          "template_id": "reminder",
          "params": {
            "first_name": "{{ user.user.name }}",
            "user_email": "{{ user.user.email }}"
          }
        }
      ]
    }
  }
}
```

## API Documentation Scraping

### Scrape OpenAPI Specs

Extract endpoints, methods, authentication, and schemas from OpenAPI/Swagger JSON files:

```bash
# POST request
curl -X POST "http://localhost:8000/scrape-openapi" \
     -H "Content-Type: application/json" \
     -d '{"openapi_url": "https://shopify.dev/api/admin-rest/2023-10/openapi.json"}'

# GET request (browser-friendly)
curl "http://localhost:8000/scrape-openapi?openapi_url=https://petstore.swagger.io/v2/swagger.json"
```

**Response:**
```json
{
  "api_name": "Shopify",
  "version_ts": "2024-01-15T10:30:00Z",
  "endpoint": "/admin/api/2023-10/products.json",
  "method": "GET",
  "auth_type": "OAuth",
  "schema_json": {
    "input": {"type": "none"},
    "output": {"type": "json", "schema": {...}}
  },
  "source_url": "https://shopify.dev/api/admin-rest/2023-10/openapi.json"
}
```

### Scrape HTML Documentation

Extract endpoints from HTML documentation pages:

```bash
# POST request
curl -X POST "http://localhost:8000/scrape-html" \
     -H "Content-Type: application/json" \
     -d '{"doc_url": "https://developers.google.com/gmail/api/reference/rest"}'

# GET request (browser-friendly)
curl "http://localhost:8000/scrape-html?doc_url=https://developers.google.com/gmail/api/reference/rest"
```

## Schema Versioning

### Store Schema Snapshots

When scraping API documentation, schemas are automatically stored in DynamoDB with timestamps for versioning.

### Retrieve Schema Versions

Get a specific schema version by API name and timestamp:

```bash
curl "http://localhost:8000/schema-snapshot?api_name=Shopify&timestamp=1705312200"
```

**Response:**
```json
{
  "api_name": "Shopify",
  "version_ts": "2024-01-15T10:30:00Z",
  "endpoint": "/admin/api/2023-10/products.json",
  "method": "GET",
  "auth_type": "OAuth",
  "schema_json": {
    "input": {"type": "none"},
    "output": {"type": "json", "schema": {...}}
  },
  "source_url": "https://shopify.dev/api/admin-rest/2023-10/openapi.json"
}
```

## Schema Diff Engine

Compare two schema versions to monitor changes:

```python
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
# Returns structured diff with additions, deletions, and changes
```

**Example Output:**
```json
{
  "added": {
    "product.tags": {
      "new_type": "string"
    }
  },
  "removed": {},
  "changed": {}
}
```

### Field Mapping

The system automatically maps common field names to standardized output fields:

| Input Field | Output Field |
|-------------|--------------|
| `name` | `first_name` |
| `email` | `user_email` |
| `signup_date` | `registration_date` |

### Supported Triggers

Common trigger events the system recognizes:
- `user_signup` - When a new user registers
- `order_placed` - When a customer places an order  
- `payment_received` - When payment is processed
- `profile_updated` - When user updates their profile
- `subscription_started` - When user subscribes to a service

### Supported Templates

Common email templates the system generates:
- `welcome` - Welcome emails for new users
- `confirmation` - Order/action confirmations
- `reminder` - Reminder notifications
- `notification` - General notifications
- `alert` - Important alerts

### Error Responses

#### 422 Validation Error
When the request payload is invalid:
```json
{
  "detail": [
    {
      "loc": ["body", "user_input"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 1}
    }
  ]
}
```

#### 500 Internal Server Error
When processing fails:
```json
{
  "detail": "Processing failed: Error description here"
}
```

### Browser Testing

For quick testing without curl, you can use your browser:

1. **Default example**: Visit `http://localhost:8000/parse-request`
2. **Custom input**: Visit `http://localhost:8000/parse-request?user_input=Your automation request here`
3. **OpenAPI scraping**: Visit `http://localhost:8000/scrape-openapi`
4. **HTML scraping**: Visit `http://localhost:8000/scrape-html`
5. **Interactive docs**: Visit `http://localhost:8000/docs` to test via Swagger UI

### Tips for Better Results

1. **Be specific about triggers**: Instead of "when something happens", use "when a user signs up" or "when an order is placed"

2. **Include field details**: Mention what information should be included (name, email, date, etc.)

3. **Specify the action**: Clearly state what should happen (send email, create task, etc.)

4. **Good examples**:
   - ✅ "When a new user registers, send a welcome email with their name and registration date"
   - ✅ "After a customer completes a purchase, send an order confirmation with order details"
   - ❌ "Do something when stuff happens"

## Testing

Run tests with:
```bash
# Install test dependencies (if not already installed)
pip install pytest httpx pytest-asyncio

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_main.py -k test_schema_diff_engine
```

## Project Structure

```
nl2flow/
├── .env                 # Environment configuration
├── setup.ps1           # PowerShell setup script
├── run.ps1             # PowerShell run script
├── run.bat             # Windows batch run script
├── run.sh              # Unix/Linux run script
├── requirements.txt    # Python dependencies
├── app/
│   ├── main.py         # FastAPI application
│   ├── gpt_handler.py  # Google Gemini integration
│   ├── models.py       # Pydantic models
│   ├── transformer.py  # Flow JSON builder
│   ├── api_doc_scraper.py  # API documentation scraper
│   ├── rules/
│   │   └── field_mapper.py  # Field mapping logic
│   ├── schemas/
│   │   └── email_flow_schema.json  # JSON schema
│   └── utils/
│       ├── logger.py   # Request logging
│       ├── validator.py # Flow validation
│       ├── dynamodb_snapshots.py  # Schema versioning
│       └── schema_diff.py  # Schema diff engine
└── tests/
    ├── test_main.py    # API tests
    └── test_transformer.py  # Transform tests
```

## Troubleshooting

### PowerShell Execution Policy
If you get an execution policy error in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Not Found
Make sure Python 3.8+ is installed and in your PATH:
- Download from https://python.org/downloads/
- During installation, check "Add Python to PATH"

### Google API Errors
- Ensure your API key is correct in the `.env` file
- Check your Google account has credits/billing set up
- The application includes fallback responses if the API is unavailable

### DynamoDB Configuration
- Ensure AWS credentials are configured (if using DynamoDB)
- The application will work without DynamoDB, but schema versioning won't be available

### Port Already in Use
If port 8000 is busy, modify the run scripts to use a different port:
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## License

MIT License - see LICENSE file for details.
