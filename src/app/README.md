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
> **Transform your ideas into automation with simple English commands!** 🚀

NL2Flow is a powerful tool that converts natural language requests into structured automation flows. Think of it as a **magic translator** that turns your everyday language into computer instructions. No programming knowledge required!

## ✨ What Can NL2Flow Do?

### 🎯 **Main Feature: Turn Words into Automation**
- **You say:** "Send a welcome email when someone signs up"
- **NL2Flow creates:** A complete automation flow that handles user signups and sends emails

### 🔍 **API Detective: Understand Other Systems**
- **You provide:** A website's API documentation URL
- **NL2Flow extracts:** All available functions (send email, get user info, etc.)

### 📊 **Change Tracker: Monitor System Updates**
- **You compare:** Two versions of the same system
- **NL2Flow reports:** What changed (like "added new field: customer phone number")

### 💾 **Smart Storage: Keep Track of Everything**
- **Automatically stores:** All API information in a secure database
- **Version control:** Track changes over time
- **Easy retrieval:** Find any information you've stored

## 🚀 Quick Start Guide

### For Non-Technical Users

#### Step 1: Get Your Computer Ready

**Windows Users:**
1. **Download** the NL2Flow folder to your computer
2. **Right-click** on the folder and select "Open PowerShell window here"
3. **Type this command** and press Enter:
   ```
   .\setup.ps1
   ```
4. **Wait** for the installation to complete

**Mac/Linux Users:**
1. **Open Terminal**
2. **Navigate** to the NL2Flow folder
3. **Type these commands** one by one:
   ```bash
   pip install -r requirements.txt
   ```

#### Step 2: Get Your API Key (One-Time Setup)

1. **Go to** [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Sign in** with your Google account
3. **Click** "Create API Key"
4. **Copy** the key (it looks like: `sk-abc123...`)

#### Step 3: Configure the Program

1. **Find the `.env` file** in your NL2Flow folder
2. **Open it** with Notepad (Windows) or TextEdit (Mac)
3. **Replace** `your_google_api_key_here` with your actual API key
4. **Save** the file

#### Step 4: Start the Program

**Windows:**
- **Double-click** `run.ps1` or type `.\run.ps1` in PowerShell

**Mac/Linux:**
- **Type** `./run.sh` in Terminal

**You'll see:**
```
Starting FastAPI server...
Server will be available at: http://localhost:8000
```

## 🌐 How to Use NL2Flow

### Method 1: Web Interface (Easiest for Beginners)

1. **Open your web browser**
2. **Go to:** `http://localhost:8000`
3. **You'll see a beautiful interface** with different options

#### Creating Your First Automation:

1. **Click** on "Try with default example" under "Parse Request"
2. **Change the text** to what you want:
   - "Send a welcome email when someone joins our website"
   - "Send order confirmation when someone buys something"
   - "Send a birthday email to customers on their birthday"
3. **Click** the button
4. **Watch the magic happen!** It creates a structured automation plan

### Method 2: Interactive API Documentation (For Power Users)

1. **Go to:** `http://localhost:8000/docs`
2. **You'll see a fancy interface** with all features
3. **Click** on any feature to try it
4. **Fill in the information** it asks for
5. **Click "Try it out"** to see the results

## 📚 Complete Feature Guide

### 🎯 Natural Language Processing

**What it does:** Converts your English requests into automation flows

**How to use:**
1. **Go to:** `http://localhost:8000/parse-request`
2. **Enter your request** in plain English
3. **Get back** a structured automation plan

**Example requests:**
- "When a new user signs up, send a welcome email with their name and signup date"
- "After a customer places an order, send them a confirmation email with order details"
- "When a payment fails, send a retry notification to the customer"
- "Send a birthday email to customers on their birthday"

### 🔍 API Documentation Scraping

**What it does:** Extracts information from other systems' documentation

**How to use:**
1. **Go to:** `http://localhost:8000/docs`
2. **Find** `POST /scrape-openapi` or `POST /scrape-html`
3. **Click** "Try it out"
4. **Enter** a documentation URL
5. **Click** "Execute"

**Popular APIs to try:**
- `https://petstore.swagger.io/v2/swagger.json` (PetStore - default)
- `https://api.github.com/v3/swagger.json` (GitHub API)
- `https://developers.google.com/gmail/api/reference/rest` (Gmail API)

### 💾 Database Storage (DynamoDB)

**What it does:** Automatically stores all API information for future use

**How it works:**
- **Automatic:** Every time you scrape an API, it's stored
- **Versioned:** Each entry has a timestamp for tracking changes
- **Searchable:** Find any information you've stored

**How to view stored data:**
1. **Go to:** `http://localhost:8000/docs`
2. **Find** `GET /schema-snapshot`
3. **Click** "Try it out"
4. **Enter** the API name and timestamp
5. **Click** "Execute"

### 📊 Schema Comparison (Diff Engine)

**What it does:** Compares two versions of the same system to see what changed

**How to use:**
1. **Go to:** `http://localhost:8000/docs`
2. **Find** `POST /diff-schemas`
3. **Click** "Try it out"
4. **Enter** two different schemas
5. **Click** "Execute"

**Example:**
```json
{
  "old_schema": {
    "product": {
      "title": "string",
      "vendor": "string"
    }
  },
  "new_schema": {
    "product": {
      "title": "string",
      "vendor": "string",
      "tags": "string"
    }
  }
}
```

**Result:** Shows that a new "tags" field was added

### 🗄️ DynamoDB Management (NEW!)

**What it does:** Manage your stored API data without logging into AWS

**Features:**
- **List all APIs:** See what APIs you have stored
- **View API versions:** See all timestamps when each API was scraped
- **Delete specific snapshots:** Remove individual API versions
- **Delete entire APIs:** Remove all data for a specific API

## 🚨 Watchdog and Alerting System (Week 3 - NEW!)

**What it does:** Automatically monitor APIs for changes and notify you when updates are detected

**Features:**
- **🕐 Scheduled Scanning:** Daily automated API scans via AWS EventBridge
- **🔍 Change Detection:** Compare current and previous schemas automatically
- **📢 Smart Notifications:** SNS alerts when changes are detected
- **📊 Admin Dashboard:** Beautiful React interface for monitoring and management
- **🔄 Manual Rescans:** Trigger immediate scans for specific APIs

### 🎯 How the Watchdog System Works

1. **Daily Automation:** EventBridge triggers Lambda function every 24 hours
2. **API Scanning:** Lambda scrapes configured APIs and stores schemas
3. **Change Detection:** Compares new schemas with previous versions
4. **Smart Alerts:** Sends SNS notifications only when changes are found
5. **Dashboard Updates:** Real-time UI shows scan status and changes

### 🛠️ Admin Dashboard Features

#### 📈 Overview Dashboard
- **Real-time metrics:** Total APIs, endpoints, success rates
- **Recent activity:** Latest changes and scan results
- **Quick actions:** Manual scans and navigation

#### 📋 API Summary
- **Comprehensive list:** All monitored APIs with status
- **Change tracking:** Added, removed, and modified endpoints
- **Rescan capability:** Manual trigger for immediate updates
- **Search and filter:** Find specific APIs quickly

#### 📊 Scan History
- **Detailed logs:** Complete scan history with timestamps
- **Success metrics:** Success rates and failure analysis
- **Performance tracking:** Scan duration and resource usage

#### 🔍 API Changes Detail
- **Version comparison:** Side-by-side schema differences
- **Change timeline:** Historical view of all modifications
- **Endpoint details:** Current schema information

### 🚀 Getting Started with Watchdog System

#### 1. Deploy AWS Infrastructure
```bash
cd infrastructure
aws cloudformation create-stack \
  --stack-name nl2flow-watchdog \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```

#### 2. Start the Dashboard
```bash
cd src/frontend
npm install
npm start
```

#### 3. Access the Dashboard
- **URL:** http://localhost:3000
- **Features:** Real-time monitoring, manual rescans, change history

#### 4. Configure SNS Notifications
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT:dev-api-schema-updated \
  --protocol email \
  --notification-endpoint your-email@example.com
```

### 📱 Dashboard API Endpoints

#### 1. Dashboard Overview
- **URL**: `GET /dashboard/scan-history`
- **Purpose**: Get recent scan history with metadata
- **Response**: List of scan results with timestamps and success rates

#### 2. API Summary
- **URL**: `GET /dashboard/api-summary`
- **Purpose**: Get summary of all APIs with their status and recent changes
- **Response**: API list with change detection and scan status

#### 3. Manual Rescan
- **URL**: `POST /dashboard/rescan-api`
- **Purpose**: Trigger immediate rescan of a specific API
- **Body**: `{"api_name": "PetStore", "openapi_url": "https://petstore.swagger.io/v2/swagger.json"}`

#### 4. API Changes Detail
- **URL**: `GET /dashboard/api-changes/{api_name}`
- **Purpose**: Get detailed change history for a specific API
- **Response**: Complete scan history and endpoint details

### 🔧 Configuration Options

#### Lambda Function Settings
```bash
# Update scan frequency (default: daily)
aws events put-rule \
  --name dev-daily-api-scan \
  --schedule-expression "rate(6 hours)"  # Every 6 hours

# Update APIs to monitor
# Edit lambda_functions/scheduled_scanner.py
apis_to_scan = [
    {'name': 'PetStore', 'url': 'https://petstore.swagger.io/v2/swagger.json'},
    {'name': 'GitHub', 'url': 'https://api.github.com/v3/swagger.json'},
    # Add your APIs here
]
```

#### SNS Notification Settings
```bash
# Add multiple email subscriptions
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT:dev-api-schema-updated \
  --protocol email \
  --notification-endpoint team@yourcompany.com

# Add Slack integration (via Lambda)
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT:dev-api-schema-updated \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:YOUR_ACCOUNT:function:slack-notifier
```

### 📊 Monitoring and Analytics

#### CloudWatch Metrics
- **Lambda invocations:** Track scan frequency and success
- **DynamoDB operations:** Monitor database performance
- **SNS delivery:** Ensure notifications are sent successfully

#### Dashboard Analytics
- **Success rates:** Track API scan reliability
- **Change frequency:** Identify APIs with frequent updates
- **Response times:** Monitor scan performance

### 🛡️ Security Features

#### AWS Security
- **IAM roles:** Least privilege access for Lambda functions
- **VPC isolation:** Optional network isolation
- **Encryption:** All data encrypted at rest and in transit

#### Dashboard Security
- **CORS protection:** Configured for secure API access
- **Input validation:** All user inputs validated
- **Error handling:** Graceful error management

### 💰 Cost Optimization

#### Free Tier Usage
- **Lambda:** 1M free requests per month
- **EventBridge:** 1M free events per month
- **SNS:** 1M free publishes per month
- **DynamoDB:** 25GB free storage

#### Cost Monitoring
```bash
# Monitor Lambda costs
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=dev-scheduled-api-scanner \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

### 🔄 Integration with AI Core

The watchdog system is designed to feed detected changes into your AI core for self-healing:

#### SNS Message Format
```json
{
  "api_name": "PetStore",
  "timestamp": 1704067200,
  "changes_summary": {
    "added_count": 2,
    "removed_count": 1,
    "modified_count": 3
  },
  "changes": {
    "added_endpoints": [
      {"path": "/pets", "method": "GET"}
    ],
    "removed_endpoints": [
      {"path": "/old-endpoint", "method": "POST"}
    ],
    "modified_endpoints": [
      {
        "path": "/pet",
        "method": "PUT",
        "old_schema": {...},
        "new_schema": {...}
      }
    ]
  }
}
```

#### AI Core Integration
```python
# Example Lambda function to handle SNS messages
def lambda_handler(event, context):
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        
        # Process changes for AI core
        if message['changes_summary']['added_count'] > 0:
            # Handle new endpoints
            handle_new_endpoints(message['api_name'], message['changes']['added_endpoints'])
        
        if message['changes_summary']['modified_count'] > 0:
            # Handle schema changes
            handle_schema_changes(message['api_name'], message['changes']['modified_endpoints'])
```

### 🎯 Success Metrics

#### User Story 1: Daily API Scans ✅
- ✅ EventBridge rule triggers Lambda daily
- ✅ Scan is idempotent, retriable, and logs last execution
- ✅ Handles multiple APIs in single scan

#### User Story 2: Change Detection and Notifications ✅
- ✅ Comparison logic runs after each scan
- ✅ SNS topic triggered for non-empty diffs
- ✅ SNS payload includes API name, diff summary, timestamp
- ✅ Detailed change information for AI core integration

#### User Story 3: Admin Dashboard ✅
- ✅ Web dashboard lists each API, last scan time, and diff summary
- ✅ UI updates in near-real-time (30-second polling)
- ✅ Includes "Rescan" button per API
- ✅ Comprehensive monitoring and management interface

**How to use:**

#### 1. List All Stored APIs
```bash
# View all APIs you have data for
curl http://localhost:8000/list-apis
```

**Or visit:** `http://localhost:8000/list-apis` in your browser

**Response:**
```json
{
  "api_names": ["PetStore", "GitHub", "Gmail"],
  "total_count": 3
}
```

#### 2. View API Versions
```bash
# See all versions of a specific API
curl http://localhost:8000/list-versions/PetStore
```

**Or visit:** `http://localhost:8000/list-versions/PetStore` in your browser

**Response:**
```json
{
  "api_name": "PetStore",
  "versions": [
    {
      "timestamp": "1704067200",
      "endpoints_count": 15,
      "methods": ["GET", "POST", "PUT", "DELETE"],
      "source_url": "https://petstore.swagger.io/v2/swagger.json",
      "auth_type": "none"
    }
  ],
  "total_count": 1
}
```

#### 3. Delete Specific Snapshot
```bash
# Delete a specific API version
curl "http://localhost:8000/delete-snapshot?api_name=PetStore&timestamp=1704067200"
```

**Or visit:** `http://localhost:8000/delete-snapshot?api_name=PetStore&timestamp=1704067200` in your browser

**Response:**
```json
{
  "message": "Successfully deleted 15 snapshot(s)",
  "api_name": "PetStore",
  "timestamp": 1704067200,
  "deleted_count": 15
}
```

#### 4. Delete Entire API
```bash
# Delete ALL data for an API
curl "http://localhost:8000/delete-api?api_name=PetStore"
```

**Or visit:** `http://localhost:8000/delete-api?api_name=PetStore` in your browser

**Response:**
```json
{
  "message": "Successfully deleted 45 snapshot(s) for API 'PetStore'",
  "api_name": "PetStore",
  "deleted_count": 45
}
```

#### 5. Advanced: Delete Specific Endpoint
```bash
# Delete only a specific endpoint from a snapshot
curl "http://localhost:8000/delete-snapshot?api_name=PetStore&timestamp=1704067200&endpoint=/pet&method=GET"
```

**Web Interface:**
1. **Go to:** `http://localhost:8000/docs`
2. **Find** the "DynamoDB Management" section
3. **Try out** any of the delete endpoints
4. **Use the browser-friendly GET versions** for easy testing

**Safety Features:**
- **No accidental deletions:** All operations require specific parameters
- **Clear feedback:** You get detailed information about what was deleted
- **Count verification:** You know exactly how many items were removed
- **Error handling:** Graceful handling of non-existent data

## 🎯 Real-World Use Cases

### 📧 Email Marketing
- **"Send a birthday email to customers on their birthday"**
- **"Send a follow-up email 3 days after someone abandons their cart"**
- **"Send a welcome series when someone subscribes to our newsletter"**

### 🛒 E-commerce
- **"Send order confirmation when someone buys something"**
- **"Send shipping updates when an order ships"**
- **"Send a review request 7 days after delivery"**

### 🎧 Customer Service
- **"Send a satisfaction survey after a support ticket is closed"**
- **"Send a welcome message when someone joins our community"**
- **"Send a reminder when someone hasn't logged in for 30 days"**

### 📊 Business Operations
- **"Send a daily report of new signups to the team"**
- **"Send an alert when inventory is low"**
- **"Send a weekly summary of sales performance"**

## 🔧 Technical Setup (For Advanced Users)

### Prerequisites
- Python 3.8 or higher
- Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Optional: AWS DynamoDB access (for schema versioning)

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
2. **Edit the `.env` file** and replace `your_google_api_key_here` with your actual API key:
   ```
   GOOGLE_API_KEY=sk-your-actual-api-key-here
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
- **Body**: `{"openapi_url": "https://petstore.swagger.io/v2/swagger.json"}`

#### 5. Scrape OpenAPI Documentation (GET)
- **URL**: `GET /scrape-openapi`
- **Purpose**: Browser-friendly OpenAPI scraper
- **Query Parameter**: `openapi_url` (optional, defaults to Petstore OpenAPI)

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

#### 11. List APIs
- **URL**: `GET /list-apis`
- **Purpose**: List all available APIs stored in DynamoDB
- **Response**: List of API names and total count

#### 12. List API Versions
- **URL**: `GET /list-versions/{api_name}`
- **Purpose**: List all versions/timestamps for a specific API
- **Response**: Version information with metadata

#### 13. Delete Snapshot (POST)
- **URL**: `DELETE /delete-snapshot`
- **Purpose**: Delete a specific schema snapshot
- **Body**: `{"api_name": "PetStore", "timestamp": 1704067200, "endpoint": "/pet", "method": "GET"}`

#### 14. Delete Snapshot (GET)
- **URL**: `GET /delete-snapshot`
- **Purpose**: Browser-friendly snapshot deletion
- **Query Parameters**: `api_name`, `timestamp`, `endpoint` (optional), `method` (optional)

#### 15. Delete API (POST)
- **URL**: `DELETE /delete-api`
- **Purpose**: Delete all snapshots for a specific API
- **Body**: `{"api_name": "PetStore"}`

#### 16. Delete API (GET)
- **URL**: `GET /delete-api`
- **Purpose**: Browser-friendly API deletion
- **Query Parameter**: `api_name`

## 📝 API Usage Examples

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

#### Example 3: List All APIs
**Request:**
```bash
curl -X GET "http://localhost:8000/list-apis"
```

**Response:**
```json
{
  "api_names": ["PetStore", "GitHub", "Gmail"],
  "total_count": 3
}
```

#### Example 4: List API Versions
**Request:**
```bash
curl -X GET "http://localhost:8000/list-versions/PetStore"
```

**Response:**
```json
{
  "api_name": "PetStore",
  "versions": [
    {
      "timestamp": "1704067200",
      "endpoints_count": 15,
      "methods": ["GET", "POST", "PUT", "DELETE"],
      "source_url": "https://petstore.swagger.io/v2/swagger.json",
      "auth_type": "none"
    }
  ],
  "total_count": 1
}
```

#### Example 5: Delete Specific Snapshot
**Request:**
```bash
curl -X DELETE "http://localhost:8000/delete-snapshot" \
     -H "Content-Type: application/json" \
     -d '{
       "api_name": "PetStore",
       "timestamp": 1704067200
     }'
```

**Response:**
```json
{
  "message": "Successfully deleted 15 snapshot(s)",
  "api_name": "PetStore",
  "timestamp": 1704067200,
  "deleted_count": 15
}
```

#### Example 6: Delete Entire API
**Request:**
```bash
curl -X DELETE "http://localhost:8000/delete-api" \
     -H "Content-Type: application/json" \
     -d '{
       "api_name": "PetStore"
     }'
```

**Response:**
```json
{
  "message": "Successfully deleted 45 snapshot(s) for API 'PetStore'",
  "api_name": "PetStore",
  "deleted_count": 45
}
```

## 🗄️ DynamoDB Integration

### What is DynamoDB?
DynamoDB is Amazon's cloud database that automatically stores all your API information. Think of it as a **smart filing cabinet** that keeps track of everything you scrape and organizes it by time and API name.

### Why Use DynamoDB?
- **Automatic Storage:** Every time you scrape an API, it's saved automatically
- **Version Control:** Track changes over time (like "what changed between January and February?")
- **Easy Search:** Find any API information you've stored
- **Free Tier Available:** 25GB storage and 25 read/write capacity units per month FREE
- **No Setup Required:** Works out of the box with the provided credentials

### 💰 DynamoDB Free Tier Information

#### What's Included in Free Tier:
- **25 GB of storage** per month
- **25 read capacity units (RCU)** per month
- **25 write capacity units (WCU)** per month
- **25 GB of data transfer** out per month
- **Valid for 12 months** from account creation

#### Free Tier Usage Tips:
- **Storage:** Each API endpoint typically uses 1-5 KB of storage
- **Read/Write:** Each scraping operation uses 1-10 read/write units
- **Cost Control:** Free tier is sufficient for testing and small projects
- **Monitoring:** Check AWS Billing Dashboard to track usage

#### When You Might Exceed Free Tier:
- **Large APIs:** APIs with 100+ endpoints
- **Frequent Scraping:** Scraping the same API multiple times daily
- **Many APIs:** Storing data from 10+ different APIs
- **Heavy Queries:** Running many searches on stored data

### 🔧 Complete AWS Setup Instructions

#### Step 1: Create AWS Account (If You Don't Have One)

1. **Go to** [AWS Console](https://aws.amazon.com/)
2. **Click** "Create an AWS Account"
3. **Fill in your details:**
   - **Email address:** Use a valid email
   - **Password:** Create a strong password
   - **AWS account name:** Choose a memorable name
4. **Complete verification** (email and phone)
5. **Add payment method** (required, but free tier won't charge you)
6. **Choose support plan:** Select "Free" plan

#### Step 2: Create IAM User (For Security)

**Why create an IAM user?**
- **Security:** Don't use your root account for applications
- **Permissions:** Limit access to only what's needed
- **Monitoring:** Track usage and costs separately

**How to create IAM user:**

1. **Sign in to AWS Console**
2. **Go to IAM service** (search "IAM" in services)
3. **Click** "Users" in the left sidebar
4. **Click** "Create user"
5. **Enter user details:**
   - **User name:** `nl2flow-user` (or any name you prefer)
   - **Access type:** Check "Programmatic access"
   - **Console access:** Leave unchecked (we only need API access)
6. **Click** "Next: Permissions"

#### Step 3: Attach Permissions Policy

**Option A: Use Existing Policy (Recommended for Beginners)**

1. **Select** "Attach existing policies directly"
2. **Search for** "DynamoDB"
3. **Check** "AmazonDynamoDBFullAccess"
4. **Click** "Next: Tags"

**Option B: Create Custom Policy (For Advanced Users)**

1. **Select** "Attach existing policies directly"
2. **Click** "Create policy"
3. **Choose** "JSON" tab
4. **Paste this policy:**
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "dynamodb:CreateTable",
                   "dynamodb:PutItem",
                   "dynamodb:GetItem",
                   "dynamodb:Query",
                   "dynamodb:Scan",
                   "dynamodb:UpdateItem",
                   "dynamodb:DeleteItem",
                   "dynamodb:DescribeTable"
               ],
               "Resource": "arn:aws:dynamodb:*:*:table/ApiSchemaSnapshots"
           }
       ]
   }
   ```
5. **Name the policy:** `NL2FlowDynamoDBPolicy`
6. **Attach it to your user**

#### Step 4: Complete User Creation

1. **Add tags** (optional):
   - **Key:** `Project`
   - **Value:** `NL2Flow`
2. **Click** "Next: Review"
3. **Review the details** and click "Create user"
4. **IMPORTANT:** Download the CSV file with credentials
5. **Save the credentials** securely (you won't see them again)

#### Step 5: Configure Environment Variables

**Update your `.env` file** with the new credentials:

```
# AWS Configuration
AWS_ACCESS_KEY_ID=your_new_access_key_here
AWS_SECRET_ACCESS_KEY=your_new_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# DynamoDB Configuration
DYNAMODB_SCHEMA_TABLE=ApiSchemaSnapshots

# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key_here
```

**Important Notes:**
- **Region:** Use `us-east-1` for best free tier availability
- **Table name:** Keep it simple and consistent
- **Security:** Never commit credentials to version control

### 🔧 DynamoDB Table Setup

#### Step 1: Choose Your Setup Method

**Option A: Using AWS Console (Recommended for Beginners)**

1. **Go to** [AWS DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. **Sign in** with your AWS account
3. **Click** "Create table"
4. **Fill in the details:**
   - **Table name:** `ApiSchemaSnapshots`
   - **Partition key:** `api_name` (String)
   - **Sort key:** `timestamp` (String)
   - **Billing mode:** **Pay per request** (recommended for free tier)
5. **Click** "Create"
6. **Wait** for the table to be created (usually takes 1-2 minutes)

**Option B: Using AWS CLI (For Advanced Users)**

1. **Install AWS CLI** from [aws.amazon.com/cli](https://aws.amazon.com/cli/)
2. **Configure AWS credentials:**
   ```bash
   aws configure
   # Enter your access key and secret key
   # Region: us-east-1
   # Output format: json
   ```
3. **Create the table:**
   ```bash
   aws dynamodb create-table \
       --table-name ApiSchemaSnapshots \
       --attribute-definitions \
           AttributeName=api_name,AttributeType=S \
           AttributeName=timestamp,AttributeType=S \
       --key-schema \
           AttributeName=api_name,KeyType=HASH \
           AttributeName=timestamp,KeyType=RANGE \
       --billing-mode PAY_PER_REQUEST
   ```

**Option C: Let the Application Create It (Automatic)**
The application will attempt to create the table automatically if it doesn't exist, but you need proper AWS permissions.

#### Step 2: Verify Table Creation

1. **Go to** [AWS DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. **Click** on "Tables" in the left sidebar
3. **Look for** `ApiSchemaSnapshots` in the list
4. **Status should be** "Active"
5. **Click** on the table name to see details

#### Step 3: Test the Setup

1. **Start your NL2Flow application:**
   ```powershell
   .\run.ps1
   ```

2. **Test with a simple API:**
   ```bash
   curl -X POST "http://localhost:8000/scrape-openapi" \
        -H "Content-Type: application/json" \
        -d '{
          "openapi_url": "https://petstore.swagger.io/v2/swagger.json"
        }'
   ```

3. **Check if data was stored:**
   - Go to AWS DynamoDB Console
   - Click on your table
   - Click "Explore table data"
   - You should see entries from the PetStore API

### 📊 How DynamoDB Works in NL2Flow

#### Automatic Storage Process
1. **You scrape an API** (using `/scrape-openapi` or `/scrape-html`)
2. **NL2Flow extracts** all endpoints and schemas
3. **Each endpoint gets stored** as a separate entry in DynamoDB
4. **Timestamp is added** for version tracking
5. **Metadata is included** (auth type, source URL, etc.)

#### What Gets Stored
Each entry contains:
- **API Name:** Identifier for the API (e.g., "PetStore", "GitHub")
- **Endpoint:** The API endpoint path (e.g., "/users", "/products")
- **Method:** HTTP method (GET, POST, PUT, DELETE)
- **Schema:** Input and output schemas in JSON format
- **Metadata:** Authentication type, source URL, version timestamp
- **Timestamp:** When the entry was created (for version tracking)

### 🚀 How to Use DynamoDB Features

#### Method 1: Add Entries via Web Interface (Easiest)

1. **Start the application:**
   ```powershell
   .\run.ps1
   ```

2. **Open your browser** and go to: `http://localhost:8000/docs`

3. **Add entries by scraping APIs:**
   - **Find** `POST /scrape-openapi`
   - **Click** "Try it out"
   - **Enter** an OpenAPI URL:
     ```json
     {
       "openapi_url": "https://petstore.swagger.io/v2/swagger.json"
     }
     ```
   - **Click** "Execute"
   - **All endpoints are automatically stored** in DynamoDB!

4. **Try HTML scraping too:**
   - **Find** `POST /scrape-html`
   - **Click** "Try it out"
   - **Enter** an HTML documentation URL:
     ```json
     {
       "doc_url": "https://developers.google.com/gmail/api/reference/rest"
     }
     ```
   - **Click** "Execute"

#### Method 2: View Stored Data

1. **Go to:** `http://localhost:8000/docs`
2. **Find** `GET /schema-snapshot`
3. **Click** "Try it out"
4. **Enter the parameters:**
   - **api_name:** The name of the API you scraped (e.g., "PetStore")
   - **timestamp:** The timestamp from the scraping response
5. **Click** "Execute"
6. **View your stored schema!**

#### Method 3: Using AWS Console (Advanced)

1. **Go to** [AWS DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. **Click** on your table name (`ApiSchemaSnapshots`)
3. **Click** "Explore table data"
4. **Browse** all your stored entries
5. **Use filters** to find specific APIs or time periods

#### Method 4: Using AWS CLI (Advanced)

```bash
# List all items in the table
aws dynamodb scan --table-name ApiSchemaSnapshots

# Query specific API
aws dynamodb query \
    --table-name ApiSchemaSnapshots \
    --key-condition-expression "api_name = :name" \
    --expression-attribute-values '{":name":{"S":"PetStore"}}'

# Query by time range
aws dynamodb query \
    --table-name ApiSchemaSnapshots \
    --key-condition-expression "api_name = :name AND #ts BETWEEN :start AND :end" \
    --expression-attribute-names '{"#ts":"timestamp"}' \
    --expression-attribute-values '{":name":{"S":"PetStore"},":start":{"S":"1704067200"},":end":{"S":"1704153600"}}'
```

### 📈 Complete Example Workflow

Here's a step-by-step example of using DynamoDB:

#### 1. Start the Application
```powershell
.\run.ps1
```

#### 2. Scrape an API (This automatically stores in DynamoDB)
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
     -d '{"openapi_url": "https://petstore.swagger.io/v2/swagger.json"}'

# GET request (browser-friendly)
curl "http://localhost:8000/scrape-openapi?openapi_url=https://petstore.swagger.io/v2/swagger.json"
```

**Response:**
```json
{
  "api_name": "Petstore",
  "version_ts": "2024-01-15T10:30:00Z",
  "endpoint": "/pet",
  "method": "GET",
  "auth_type": "api_key",
  "schema_json": {
    "input": {"type": "none"},
    "output": {"type": "json", "schema": {...}}
  },
  "source_url": "https://petstore.swagger.io/v2/swagger.json"
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
3. **OpenAPI scraping**: Visit `http://localhost:8000/scrape-openapi` (uses Petstore API)
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
NL2Flow/
├── src/
│   ├── app/
│   └── frontend/
├── tests/
│   ├── __init__.py
│   ├── test_main.py            # Main API tests
│   ├── test_transformer.py     # Transformer tests
│   └── test_order_confirmation.py
├── scripts/
│   └── compile_pyke_rules.py
├── requirements.txt            # Python dependencies
├── run.ps1                     # Windows PowerShell runner
├── run.bat                     # Windows Command Prompt runner
├── run.sh                      # Unix/Linux/macOS runner
├── setup.ps1                   # Windows setup script
└── README.md                   # This file
```

## 🐛 Troubleshooting

### Common Issues

#### ❌ **"Server won't start"**
- **Check:** Did you install Python? (Download from python.org)
- **Check:** Did you run the setup script?
- **Check:** Is port 8000 already in use? (Try closing other programs)

#### ❌ **"API key error"**
- **Check:** Did you put your API key in the .env file?
- **Check:** Is the API key correct? (Copy it exactly from Google AI Studio)
- **Check:** Do you have internet connection?

#### ❌ **"Can't access the website"**
- **Check:** Is the server running? (You should see "Server will be available at: http://localhost:8000")
- **Check:** Are you going to the right URL? (http://localhost:8000)
- **Check:** Is your firewall blocking it?

#### ❌ **"DynamoDB table doesn't exist"**
- **Solution:** Create the DynamoDB table first
- **Check:** AWS credentials are properly configured
- **Required permissions:** `dynamodb:CreateTable`, `dynamodb:PutItem`, `dynamodb:Query`, `dynamodb:Scan`

#### ❌ **"Access Denied" for DynamoDB**
- **Solution:** Verify your AWS credentials have DynamoDB permissions
- **Check:** AWS region configuration
- **Check:** Firewall settings

### Getting Help

- **Check the logs** in your terminal for error messages
- **Try the health check** at `http://localhost:8000/health`
- **Look at the interactive docs** at `http://localhost:8000/docs`
- **Run the tests** to verify everything is working

## 💡 Tips for Success

### 🎯 **Write Clear Requests**
- **Good:** "Send a welcome email when someone signs up"
- **Bad:** "Do the email thing for new people"

### 🎯 **Be Specific**
- **Good:** "Send a welcome email with their first name and signup date"
- **Bad:** "Send an email"

### 🎯 **Think About Triggers**
- **Good:** "When someone places an order, send confirmation"
- **Bad:** "Send confirmation emails"

### 🎯 **Use the Web Interface**
- Start with `http://localhost:8000` for the easiest experience
- Use `http://localhost:8000/docs` for advanced features
- Try the browser-friendly endpoints first

## 🚀 What's Next?

Once you're comfortable with the basics, you can:

1. **Explore the API documentation** at `/docs` to see all features
2. **Try different types of automations**
3. **Experiment with API scraping** to understand other systems
4. **Use the schema diff tool** to track changes in your systems
5. **Integrate with your existing workflows**

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Google Gemini](https://ai.google.dev/)
- Schema validation with [JSON Schema](https://json-schema.org/)
- Database storage with [AWS DynamoDB](https://aws.amazon.com/dynamodb/)

---

**Remember:** NL2Flow is designed to be **simple and intuitive**. If something doesn't work, it's usually a small configuration issue that's easy to fix. Don't be afraid to experiment and try different things!

The beauty of this tool is that you don't need to be a programmer to create powerful automations. You just need to be able to describe what you want in plain English! 🎉
