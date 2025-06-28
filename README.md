# NL2Flow: Natural Language to Automation Flow Generator

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

### Configuration

1. **Get a Google API key** from https://makersuite.google.com/app/apikey
2. **Edit the `.env` file** and replace `your_google_api_key_here` with your actual API key:
   ```
   GOOGLE_API_KEY=sk-your-actual-api-key-here
   ```
3. **Optional: Configure DynamoDB** (for schema versioning):
   ```
   DYNAMODB_SCHEMA_TABLE=ApiSchemaSnapshots
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_DEFAULT_REGION=us-east-1
   ```

## 🌐 API Endpoints

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

#### 9. Diff Schemas
- **URL**: `POST /diff-schemas`
- **Purpose**: Compare two schema versions and get structured differences
- **Body**: `{"old_schema": {...}, "new_schema": {...}}`

#### 10. Interactive Documentation
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
```bash
curl -X POST "http://localhost:8000/scrape-openapi" \
     -H "Content-Type: application/json" \
     -d '{
       "openapi_url": "https://petstore.swagger.io/v2/swagger.json"
     }'
```

**Response includes:**
```json
{
  "trace_id": "...",
  "api_name": "PetStore",
  "version_ts": "2024-01-01T12:00:00Z",
  "endpoint": "/pet",
  "method": "GET",
  "auth_type": "none",
  "schema_json": {...},
  "source_url": "https://petstore.swagger.io/v2/swagger.json"
}
```

#### 3. Check What Was Stored
```bash
# Get the timestamp from the response above, then:
curl "http://localhost:8000/schema-snapshot?api_name=PetStore&timestamp=1704067200"
```

#### 4. Add More APIs
```bash
# Scrape GitHub API
curl -X POST "http://localhost:8000/scrape-openapi" \
     -H "Content-Type: application/json" \
     -d '{
       "openapi_url": "https://api.github.com/v3/swagger.json"
     }'

# Scrape Gmail API (HTML)
curl -X POST "http://localhost:8000/scrape-html" \
     -H "Content-Type: application/json" \
     -d '{
       "doc_url": "https://developers.google.com/gmail/api/reference/rest"
     }'
```

### 🔍 Popular APIs to Scrape and Store

#### OpenAPI Specs (JSON):
- `https://petstore.swagger.io/v2/swagger.json` (PetStore - default)
- `https://api.github.com/v3/swagger.json` (GitHub API)
- `https://api.stripe.com/v1/swagger.json` (Stripe API)
- `https://api.slack.com/openapi/v2/slack_web.json` (Slack API)
- `https://api.twitter.com/2/openapi.json` (Twitter API)

#### HTML Documentation:
- `https://developers.google.com/gmail/api/reference/rest` (Gmail API - default)
- `https://docs.shopify.com/api/admin-rest` (Shopify API)
- `https://developer.twitter.com/en/docs/api-reference-index` (Twitter API)
- `https://docs.github.com/en/rest` (GitHub REST API)

### 📊 Understanding Your Data

#### Table Structure
```
ApiSchemaSnapshots Table:
├── api_name (Partition Key)
│   ├── PetStore
│   ├── GitHub
│   ├── Gmail
│   └── ...
└── timestamp (Sort Key)
    ├── 1704067200 (Jan 1, 2024)
    ├── 1704153600 (Jan 2, 2024)
    └── ...
```

#### Sample Entry
```json
{
  "api_name": "PetStore",
  "timestamp": "1704067200",
  "endpoint": "/pet",
  "method": "GET",
  "schema": {
    "input": {"type": "none"},
    "output": {"type": "json", "status_code": "200"}
  },
  "metadata": {
    "auth_type": "none",
    "source_url": "https://petstore.swagger.io/v2/swagger.json",
    "version_ts": "2024-01-01T12:00:00Z"
  }
}
```

### 🛠️ Advanced DynamoDB Features

#### Manual Entry Addition (For Developers)
If you want to manually add entries without scraping:

```python
from app.utils.dynamodb_snapshots import store_schema_snapshot
import time

# Add a manual entry
store_schema_snapshot(
    api_name="MyCustomAPI",
    endpoint="/users",
    method="GET",
    schema={
        "input": {"type": "none"},
        "output": {"type": "json", "status_code": "200"}
    },
    metadata={
        "auth_type": "bearer_token",
        "source_url": "https://myapi.com/docs",
        "version_ts": "2024-01-01T00:00:00Z"
    },
    timestamp=int(time.time())
)
```

#### Batch Operations
To add multiple APIs quickly:
1. Use `GET /scrape-openapi` for each API
2. Each execution adds ALL endpoints from that API
3. No need to manually specify each endpoint

#### Version Tracking
- Each scraping creates a new version with a timestamp
- Use the `version_ts` to track when schemas were added
- Compare versions using the diff engine

### 🐛 DynamoDB Troubleshooting

#### ❌ **"Table doesn't exist" Error**
- **Solution:** Create the DynamoDB table first (see Step 3 above)
- **Check:** AWS credentials are properly configured
- **Check:** Table name matches `DYNAMODB_SCHEMA_TABLE` in `.env`

#### ❌ **"Access Denied" Error**
- **Solution:** Verify your AWS credentials have DynamoDB permissions
- **Required permissions:** `dynamodb:CreateTable`, `dynamodb:PutItem`, `dynamodb:Query`, `dynamodb:Scan`
- **Check:** AWS region configuration
- **Check:** Firewall settings

#### ❌ **"No entries found"**
- **Check:** Did you actually scrape an API? (The storage only happens during scraping)
- **Check:** Are you using the correct table name?
- **Check:** Are you querying with the correct API name and timestamp?
- **Check:** The scraping response for the correct values

#### ❌ **"Connection timeout"**
- **Check:** Internet connection
- **Check:** AWS region configuration
- **Check:** Firewall settings
- **Check:** AWS service status

#### ❌ **"Invalid credentials"**
- **Check:** AWS access key and secret key are correct
- **Check:** Credentials are properly set in `.env` file
- **Check:** AWS account is active and not suspended

#### ❌ **"Free tier exceeded"**
- **Check:** AWS Billing Dashboard for usage
- **Solution:** Wait for next month or upgrade to paid tier
- **Monitor:** Set up billing alerts to avoid surprises

### 💡 DynamoDB Best Practices

#### 🎯 **Naming Conventions**
- **API Names:** Use consistent naming (e.g., "PetStore", "GitHub", "Gmail")
- **Timestamps:** Use Unix timestamps for easy sorting
- **Endpoints:** Include leading slash (e.g., "/users", not "users")

#### 🎯 **Data Organization**
- **Group related APIs:** Use similar naming for related services
- **Regular scraping:** Set up regular scraping to track API changes
- **Clean up old data:** Periodically remove outdated entries

#### 🎯 **Performance Tips**
- **Batch operations:** Scrape multiple APIs in one session
- **Efficient queries:** Use specific API names and time ranges
- **Monitor usage:** Check AWS CloudWatch for performance metrics

#### 🎯 **Free Tier Optimization**
- **Limit scraping frequency:** Don't scrape the same API multiple times daily
- **Choose smaller APIs:** Start with APIs that have fewer endpoints
- **Monitor storage:** Keep track of your 25GB limit
- **Use pay-per-request:** More cost-effective for variable workloads

### 🔒 Security Considerations

#### AWS Credentials
- **Keep credentials secure:** Don't share your AWS keys
- **Use IAM roles:** For production, use IAM roles instead of access keys
- **Rotate keys:** Regularly rotate your AWS access keys
- **Least privilege:** Only grant necessary DynamoDB permissions

#### Data Privacy
- **Sensitive data:** Be careful not to store sensitive information
- **API keys:** Don't store actual API keys in schemas
- **Access control:** Use AWS IAM to control who can access your data

### 📊 Monitoring and Analytics

#### AWS CloudWatch
- **Monitor table metrics:** Check read/write capacity
- **Set up alarms:** Get notified of high usage
- **Track costs:** Monitor DynamoDB costs

#### AWS Billing Dashboard
- **Track free tier usage:** Monitor your 25GB storage and 25 RCU/WCU
- **Set up billing alerts:** Get notified when approaching limits
- **Review monthly charges:** Ensure you stay within free tier

#### Application Logs
- **Check application logs:** For DynamoDB operation errors
- **Monitor performance:** Track response times
- **Debug issues:** Use logs to troubleshoot problems

---

**Remember:** DynamoDB storage happens automatically when you use the API scraping features. You don't need to manually manage the database - just scrape APIs and the system will store everything for you! The free tier is perfect for testing and small projects. 🚀

## 🧪 Testing

Run the test suite to verify everything is working:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_main.py

# Run with verbose output
pytest -v
```

## 📁 Project Structure

```
NL2Flow/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Data models
│   ├── gpt_handler.py          # Google Gemini integration
│   ├── transformer.py          # Flow generation logic
│   ├── api_doc_scraper.py      # API documentation scraping
│   ├── rules/
│   │   ├── __init__.py
│   │   ├── field_mapper.py     # Field mapping rules
│   │   └── field_mapping.krb   # Knowledge base
│   ├── schemas/
│   │   └── email_flow_schema.json
│   ├── static/
│   │   └── favicon.ico
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # Request logging
│       ├── validator.py        # Schema validation
│       ├── dynamodb_snapshots.py  # Schema versioning
│       └── schema_diff.py      # Schema comparison
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
