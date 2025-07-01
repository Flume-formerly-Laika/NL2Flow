# NL2Flow Week 3: Watchdog and Alerting System Deployment Guide

This guide covers the deployment of the Week 3 deliverables including AWS EventBridge, Lambda functions, SNS notifications, and the React admin dashboard.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   EventBridge   │───▶│   Lambda        │───▶│   DynamoDB      │
│   (Daily)       │    │   Scanner       │    │   Tables        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   SNS Topic     │
                       │   (Alerts)      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   React         │
                       │   Dashboard     │
                       └─────────────────┘
```

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Node.js** (v16+) and **npm** for React dashboard
4. **Python** (3.8+) for Lambda functions
5. **Docker** (optional, for containerized deployment)

## 🚀 Deployment Steps

### Step 1: Deploy AWS Infrastructure

1. **Navigate to the infrastructure directory:**
   ```bash
   cd infrastructure
   ```

2. **Deploy CloudFormation stack:**
   ```bash
   aws cloudformation create-stack \
     --stack-name nl2flow-watchdog \
     --template-body file://cloudformation.yaml \
     --parameters ParameterKey=Environment,ParameterValue=dev \
     --capabilities CAPABILITY_NAMED_IAM
   ```

3. **Wait for stack creation:**
   ```bash
   aws cloudformation wait stack-create-complete \
     --stack-name nl2flow-watchdog
   ```

4. **Get stack outputs:**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name nl2flow-watchdog \
     --query 'Stacks[0].Outputs'
   ```

### Step 2: Deploy Lambda Function

1. **Create deployment package:**
   ```bash
   cd lambda_functions
   pip install -r requirements.txt -t .
   zip -r scheduled_scanner.zip .
   ```

2. **Update Lambda function:**
   ```bash
   aws lambda update-function-code \
     --function-name dev-scheduled-api-scanner \
     --zip-file fileb://scheduled_scanner.zip
   ```

3. **Update environment variables:**
   ```bash
   aws lambda update-function-configuration \
     --function-name dev-scheduled-api-scanner \
     --environment Variables='{
       "DYNAMODB_SCHEMA_TABLE": "ApiSchemaSnapshots",
       "SCAN_METADATA_TABLE": "ApiScanMetadata",
       "SNS_TOPIC_ARN": "arn:aws:sns:us-east-1:YOUR_ACCOUNT:dev-api-schema-updated"
     }'
   ```

### Step 3: Deploy React Dashboard

1. **Navigate to dashboard directory:**
   ```bash
   cd dashboard/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

4. **Deploy to S3 (optional):**
   ```bash
   aws s3 sync build/ s3://your-dashboard-bucket --delete
   aws s3 website s3://your-dashboard-bucket --index-document index.html
   ```

### Step 4: Configure SNS Subscriptions

1. **Create email subscription:**
   ```bash
   aws sns subscribe \
     --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT:dev-api-schema-updated \
     --protocol email \
     --notification-endpoint your-email@example.com
   ```

2. **Create Lambda subscription (for AI core integration):**
   ```bash
   aws sns subscribe \
     --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT:dev-api-schema-updated \
     --protocol lambda \
     --notification-endpoint arn:aws:lambda:us-east-1:YOUR_ACCOUNT:function:ai-core-handler
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the dashboard directory:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_AWS_REGION=us-east-1
REACT_APP_SNS_TOPIC_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT:dev-api-schema-updated
```

### Lambda Configuration

Update the Lambda function configuration:

```bash
aws lambda update-function-configuration \
  --function-name dev-scheduled-api-scanner \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables='{
    "DYNAMODB_SCHEMA_TABLE": "ApiSchemaSnapshots",
    "SCAN_METADATA_TABLE": "ApiScanMetadata",
    "SNS_TOPIC_ARN": "arn:aws:sns:us-east-1:YOUR_ACCOUNT:dev-api-schema-updated",
    "ENVIRONMENT": "dev"
  }'
```

## 🧪 Testing

### Test Lambda Function

1. **Create test event:**
   ```json
   {
     "source": "aws.events",
     "detail-type": "Scheduled Event",
     "detail": {}
   }
   ```

2. **Invoke Lambda:**
   ```bash
   aws lambda invoke \
     --function-name dev-scheduled-api-scanner \
     --payload file://test-event.json \
     response.json
   ```

3. **Check logs:**
   ```bash
   aws logs tail /aws/lambda/dev-scheduled-api-scanner --follow
   ```

### Test SNS Notifications

1. **Publish test message:**
   ```bash
   aws sns publish \
     --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT:dev-api-schema-updated \
     --message '{"test": "message"}' \
     --subject "Test Notification"
   ```

### Test Dashboard

1. **Start development server:**
   ```bash
   cd dashboard/frontend
   npm start
   ```

2. **Access dashboard:**
   - Open http://localhost:3000
   - Navigate through different sections
   - Test API rescan functionality

## 📊 Monitoring

### CloudWatch Metrics

Monitor the following metrics:

- **Lambda invocations and errors**
- **DynamoDB read/write capacity**
- **SNS message delivery**
- **EventBridge rule triggers**

### Dashboard Metrics

The React dashboard provides:

- **Real-time API status**
- **Scan history and success rates**
- **Change detection summaries**
- **Manual rescan capabilities**

## 🔒 Security

### IAM Permissions

Ensure the following permissions are configured:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/ApiSchemaSnapshots",
        "arn:aws:dynamodb:*:*:table/ApiScanMetadata"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:us-east-1:*:*-api-schema-updated"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### Network Security

- **VPC configuration** (if required)
- **Security groups** for Lambda functions
- **CORS configuration** for dashboard API

## 🚨 Troubleshooting

### Common Issues

1. **Lambda timeout:**
   - Increase timeout to 300 seconds
   - Check network connectivity to external APIs

2. **DynamoDB errors:**
   - Verify table names and permissions
   - Check for reserved keywords in queries

3. **SNS delivery failures:**
   - Verify topic ARN and permissions
   - Check subscription status

4. **Dashboard connection issues:**
   - Verify API base URL configuration
   - Check CORS settings on FastAPI server

### Logs and Debugging

1. **Lambda logs:**
   ```bash
   aws logs tail /aws/lambda/dev-scheduled-api-scanner --follow
   ```

2. **CloudWatch metrics:**
   ```bash
   aws cloudwatch get-metric-statistics \
     --namespace AWS/Lambda \
     --metric-name Invocations \
     --dimensions Name=FunctionName,Value=dev-scheduled-api-scanner \
     --start-time 2024-01-01T00:00:00Z \
     --end-time 2024-01-02T00:00:00Z \
     --period 3600 \
     --statistics Sum
   ```

## 📈 Scaling Considerations

### Performance Optimization

1. **Lambda concurrency limits**
2. **DynamoDB read/write capacity**
3. **SNS message delivery**
4. **Dashboard polling frequency**

### Cost Optimization

1. **Lambda execution time optimization**
2. **DynamoDB storage optimization**
3. **SNS message filtering**
4. **CloudWatch log retention**

## 🔄 Maintenance

### Regular Tasks

1. **Monitor CloudWatch metrics**
2. **Review Lambda logs**
3. **Update API endpoints list**
4. **Clean up old scan metadata**

### Updates and Upgrades

1. **Lambda function updates**
2. **Dashboard feature updates**
3. **Infrastructure improvements**
4. **Security patches**

## 📞 Support

For issues and questions:

1. **Check CloudWatch logs**
2. **Review Lambda function code**
3. **Verify AWS permissions**
4. **Test individual components**

## 🎯 Success Criteria

### User Story 1: Daily API Scans ✅
- [x] EventBridge rule triggers Lambda daily
- [x] Scan is idempotent and retriable
- [x] Last execution is logged

### User Story 2: Change Detection and Notifications ✅
- [x] Comparison logic runs after each scan
- [x] SNS topic triggered for non-empty diffs
- [x] SNS payload includes API name, diff summary, timestamp

### User Story 3: Admin Dashboard ✅
- [x] Web dashboard lists APIs and scan times
- [x] UI updates in near-real-time
- [x] Includes "Rescan" button per API

## 🚀 Next Steps

1. **Production deployment**
2. **Additional API integrations**
3. **Advanced change detection**
4. **Machine learning integration**
5. **Automated remediation** 