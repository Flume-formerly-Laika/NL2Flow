# NL2Flow - API Watchdog and Alerting System

A comprehensive system for monitoring API schema changes, automated scanning, and alerting with a modern React admin dashboard.

## 🚀 Features

### ✅ Deliverable 1: EventBridge Daily Scans
- **Automated Scanning**: Lambda function triggered daily by EventBridge
- **Multi-API Support**: Configurable list of APIs to monitor
- **Retry Logic**: Robust error handling with exponential backoff
- **CloudWatch Logging**: Comprehensive logging for monitoring and debugging

### ✅ Deliverable 2: Schema Comparison & SNS Notifications
- **Detailed Diff Engine**: Field-level schema comparison
- **SNS Integration**: Real-time notifications for schema changes
- **Structured Alerts**: Rich notification payloads with change details
- **Change Classification**: Added, removed, and modified endpoint detection

### ✅ Deliverable 3: Admin Dashboard (React)
- **Modern UI**: React-based dashboard with Tailwind CSS
- **Real-time Updates**: Auto-refresh and manual refresh capabilities
- **Multi-view Navigation**: Dashboard, Scan History, API Changes, Settings
- **Interactive Features**: Manual rescan, detailed change views, status indicators

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   EventBridge   │───▶│   Lambda        │───▶│   DynamoDB      │
│   (Daily Trig)  │    │   Scanner       │    │   Schema Store  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   SNS Topic     │
                       │   (Alerts)      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   FastAPI       │◄───│   React         │
                       │   Backend       │    │   Dashboard     │
                       └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- AWS CLI configured
- AWS account with appropriate permissions

## 🛠️ Installation & Setup

### 1. Clone and Setup

```bash
git clone <repository-url>
cd NL2Flow
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r src/app/requirements.txt

# Set environment variables
export DYNAMODB_SCHEMA_TABLE=ApiSchemaSnapshots
export SCAN_METADATA_TABLE=ApiScanMetadata
export SNS_TOPIC_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT:api-schema-updated
export ENVIRONMENT=dev

# Configure AWS credentials
aws configure
```

### 3. Frontend Setup

```bash
cd src/frontend

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_API_BASE_URL=http://localhost:8000" > .env
```

### 4. AWS Infrastructure

```bash
# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file infrastructure/cloudformation.yaml \
  --stack-name nl2flow-stack \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides Environment=dev
```

## 🚀 Running the Application

### Backend (FastAPI)

```bash
# From project root
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the provided script
./run.ps1  # Windows PowerShell
./run.sh   # Linux/Mac
```

**Backend will be available at:**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Frontend (React)

```bash
cd src/frontend
npm start
```

**Frontend will be available at:**
- Dashboard: http://localhost:3000

## 📊 Dashboard Features

### Main Dashboard
- **API Summary Table**: Shows all monitored APIs with status and recent changes
- **Statistics Cards**: Total APIs, successful scans, changes detected, last scan time
- **Manual Rescan**: Trigger immediate scans for specific APIs
- **Real-time Updates**: Auto-refresh every 30 seconds

### Scan History
- **Chronological View**: Timeline of all scan executions
- **Success/Failure Rates**: Performance metrics and error tracking
- **Detailed Results**: Individual API scan results and endpoints

### API Changes
- **Detailed Diff View**: Field-level change detection
- **Change Classification**: Added, removed, and modified endpoints
- **Schema Comparison**: Before/after schema visualization
- **Filter Options**: Filter by change type

### Settings
- **Configuration**: API endpoints, refresh intervals, scan limits
- **System Information**: Version, environment, connection status
- **Environment Variables**: Current configuration display

## 🔧 Configuration

### Environment Variables

**Backend (.env or environment variables):**
```env
DYNAMODB_SCHEMA_TABLE=ApiSchemaSnapshots
SCAN_METADATA_TABLE=ApiScanMetadata
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT:api-schema-updated
ENVIRONMENT=dev
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

**Frontend (.env):**
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_AWS_REGION=us-east-1
REACT_APP_SNS_TOPIC_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT:api-schema-updated
```

### API Configuration

Edit `src/app/lambda_functions/scheduled_scanner.py` to configure APIs:

```python
apis_to_scan = [
    APIConfig(
        name='PetStore',
        url='https://petstore.swagger.io/v2/swagger.json',
        description='Swagger Petstore API'
    ),
    APIConfig(
        name='GitHub',
        url='https://api.github.com/v3/swagger.json',
        description='GitHub REST API'
    ),
    # Add more APIs here
]
```

## 🧪 Testing

### Test Lambda Function

```bash
# Create test event
cat > test-event.json << EOF
{
  "source": "aws.events",
  "detail-type": "Scheduled Event",
  "detail": {}
}
EOF

# Invoke Lambda
aws lambda invoke \
  --function-name dev-scheduled-api-scanner \
  --payload file://test-event.json \
  response.json
```

### Test SNS Notifications

```bash
# Subscribe to SNS topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT:dev-api-schema-updated \
  --protocol email \
  --notification-endpoint your-email@example.com
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API summary
curl http://localhost:8000/dashboard/api-summary

# Scan history
curl http://localhost:8000/dashboard/scan-history
```

## 📈 Monitoring

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/dev-scheduled-api-scanner --follow

# View metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=dev-scheduled-api-scanner \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

### Dashboard Monitoring

- **Real-time Status**: View API status and scan results
- **Error Tracking**: Monitor failed scans and errors
- **Performance Metrics**: Track scan duration and success rates
- **Change Detection**: Monitor schema change frequency

## 🔍 Troubleshooting

### Common Issues

1. **Lambda Timeout**
   - Increase timeout in CloudFormation template
   - Check network connectivity to external APIs
   - Monitor scan duration in logs

2. **DynamoDB Errors**
   - Verify table names and permissions
   - Check for reserved keywords in queries
   - Monitor read/write capacity

3. **SNS Delivery Failures**
   - Verify topic ARN and permissions
   - Check subscription status
   - Monitor message delivery metrics

4. **Dashboard Connection Issues**
   - Verify API base URL configuration
   - Check CORS settings on backend
   - Monitor network requests in browser

### Debugging Tips

1. **Check Logs**
   ```bash
   # Lambda logs
   aws logs tail /aws/lambda/dev-scheduled-api-scanner --follow
   
   # Backend logs
   # Check console output when running uvicorn
   ```

2. **Test Individual Components**
   ```bash
   # Test API scraping
   curl http://localhost:8000/scrape-openapi?openapi_url=https://petstore.swagger.io/v2/swagger.json
   
   # Test schema comparison
   curl -X POST http://localhost:8000/diff-schemas \
     -H "Content-Type: application/json" \
     -d '{"old_schema": {}, "new_schema": {}}'
   ```

3. **Verify AWS Permissions**
   ```bash
   # Test DynamoDB access
   aws dynamodb scan --table-name ApiSchemaSnapshots --limit 1
   
   # Test SNS access
   aws sns list-topics
   ```

## 📚 API Documentation

### Dashboard Endpoints

- `GET /dashboard/api-summary` - Get API summary and status
- `GET /dashboard/scan-history` - Get scan execution history
- `POST /dashboard/rescan-api` - Trigger manual rescan
- `GET /dashboard/api-changes/{api_name}` - Get detailed changes for API

### Core Endpoints

- `GET /health` - Health check
- `POST /scrape-openapi` - Scrape OpenAPI specification
- `POST /diff-schemas` - Compare schema versions
- `GET /list-apis` - List all monitored APIs

### Interactive Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## 🔄 Deployment

### Production Deployment

1. **Update Environment Variables**
   ```bash
   export ENVIRONMENT=prod
   export SNS_TOPIC_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT:prod-api-schema-updated
   ```

2. **Deploy Infrastructure**
   ```bash
   aws cloudformation deploy \
     --template-file infrastructure/cloudformation.yaml \
     --stack-name nl2flow-prod \
     --parameter-overrides Environment=prod
   ```

3. **Deploy Frontend**
   ```bash
   cd src/frontend
   npm run build
   # Deploy build folder to your hosting service
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review CloudWatch logs
3. Test individual components
4. Create an issue with detailed information

## 🎯 Success Criteria

### ✅ User Story 1: Daily API Scans
- [x] EventBridge rule triggers Lambda daily
- [x] Lambda scans all configured APIs
- [x] CloudWatch logs show successful execution
- [x] Retry logic handles failures

### ✅ User Story 2: Schema Comparison & Notifications
- [x] System compares new vs previous schemas
- [x] SNS notifications sent for changes
- [x] Detailed diff information included
- [x] Change classification (added/removed/modified)

### ✅ User Story 3: Admin Dashboard
- [x] React-based dashboard with modern UI
- [x] API status and scan history display
- [x] Manual rescan functionality
- [x] Detailed change visualization
- [x] Real-time updates and notifications

### ✅ Additional Features
- [x] DynamoDB schema versioning
- [x] CloudWatch monitoring
- [x] Comprehensive error handling
- [x] Responsive design
- [x] CORS configuration
- [x] Environment-based configuration 