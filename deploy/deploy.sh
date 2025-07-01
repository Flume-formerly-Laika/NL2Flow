#!/bin/bash

# NL2Flow Week 3 Deployment Script
# Deploys the Watchdog and Alerting System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="nl2flow-watchdog"
ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}

echo -e "${BLUE}🚀 NL2Flow Week 3 Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}Region: ${REGION}${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials are not configured. Please run 'aws configure' first."
    exit 1
fi

print_status "AWS CLI is configured"

# Check if CloudFormation template exists
if [ ! -f "infrastructure/cloudformation.yaml" ]; then
    print_error "CloudFormation template not found at infrastructure/cloudformation.yaml"
    exit 1
fi

print_status "CloudFormation template found"

# Deploy CloudFormation stack
echo ""
echo "🏗️  Deploying AWS infrastructure..."

# Check if stack already exists
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &> /dev/null; then
    print_warning "Stack $STACK_NAME already exists. Updating..."
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://infrastructure/cloudformation.yaml \
        --parameters ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
    
    echo "Waiting for stack update to complete..."
    aws cloudformation wait stack-update-complete \
        --stack-name $STACK_NAME \
        --region $REGION
else
    print_status "Creating new stack $STACK_NAME..."
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://infrastructure/cloudformation.yaml \
        --parameters ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
    
    echo "Waiting for stack creation to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name $STACK_NAME \
        --region $REGION
fi

print_status "CloudFormation stack deployed successfully"

# Get stack outputs
echo ""
echo "📋 Getting stack outputs..."
OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output json)

echo "$OUTPUTS" > stack-outputs.json
print_status "Stack outputs saved to stack-outputs.json"

# Deploy Lambda function
echo ""
echo "🔧 Deploying Lambda function..."

# Check if Lambda function exists
LAMBDA_FUNCTION_NAME="${ENVIRONMENT}-scheduled-api-scanner"

if [ ! -f "lambda_functions/requirements.txt" ]; then
    print_error "Lambda requirements.txt not found"
    exit 1
fi

# Create deployment package
echo "Creating Lambda deployment package..."
cd lambda_functions

# Install dependencies
pip install -r requirements.txt -t . --quiet

# Create ZIP file
zip -r scheduled_scanner.zip . -x "*.pyc" "__pycache__/*" "*.git*" > /dev/null

# Update Lambda function code
echo "Updating Lambda function code..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --zip-file fileb://scheduled_scanner.zip \
    --region $REGION

# Update Lambda configuration
echo "Updating Lambda configuration..."
aws lambda update-function-configuration \
    --function-name $LAMBDA_FUNCTION_NAME \
    --timeout 300 \
    --memory-size 512 \
    --environment Variables="{
        \"DYNAMODB_SCHEMA_TABLE\": \"ApiSchemaSnapshots\",
        \"SCAN_METADATA_TABLE\": \"ApiScanMetadata\",
        \"SNS_TOPIC_ARN\": \"arn:aws:sns:${REGION}:$(aws sts get-caller-identity --query Account --output text):${ENVIRONMENT}-api-schema-updated\",
        \"ENVIRONMENT\": \"${ENVIRONMENT}\"
    }" \
    --region $REGION

cd ..
print_status "Lambda function deployed successfully"

# Test Lambda function
echo ""
echo "🧪 Testing Lambda function..."
TEST_EVENT='{"source": "aws.events", "detail-type": "Scheduled Event", "detail": {}}'
echo "$TEST_EVENT" > test-event.json

aws lambda invoke \
    --function-name $LAMBDA_FUNCTION_NAME \
    --payload file://test-event.json \
    --region $REGION \
    response.json

if [ $? -eq 0 ]; then
    print_status "Lambda function test successful"
    echo "Response: $(cat response.json)"
else
    print_warning "Lambda function test failed. Check CloudWatch logs for details."
fi

# Clean up test files
rm -f test-event.json response.json

# Deploy React Dashboard
echo ""
echo "📊 Deploying React Dashboard..."

if [ ! -d "dashboard/frontend" ]; then
    print_error "Dashboard frontend directory not found"
    exit 1
fi

cd dashboard/frontend

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_warning "Node.js is not installed. Skipping dashboard deployment."
    cd ../..
else
    # Install dependencies
    echo "Installing dashboard dependencies..."
    npm install --silent
    
    # Build for production
    echo "Building dashboard..."
    npm run build
    
    print_status "Dashboard built successfully"
    echo "Dashboard files are ready in the build/ directory"
    echo "You can deploy them to S3 or serve them locally with: npm start"
    
    cd ../..
fi

# Create SNS subscription (optional)
echo ""
echo "📧 Setting up SNS notifications..."

read -p "Would you like to set up email notifications? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter email address for notifications: " EMAIL_ADDRESS
    
    SNS_TOPIC_ARN="arn:aws:sns:${REGION}:$(aws sts get-caller-identity --query Account --output text):${ENVIRONMENT}-api-schema-updated"
    
    aws sns subscribe \
        --topic-arn $SNS_TOPIC_ARN \
        --protocol email \
        --notification-endpoint $EMAIL_ADDRESS \
        --region $REGION
    
    print_status "Email subscription created. Please check your email to confirm."
fi

# Final summary
echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo "📋 Summary:"
echo "  • CloudFormation stack: $STACK_NAME"
echo "  • Lambda function: $LAMBDA_FUNCTION_NAME"
echo "  • Environment: $ENVIRONMENT"
echo "  • Region: $REGION"
echo ""
echo "🔗 Useful commands:"
echo "  • View stack outputs: cat stack-outputs.json"
echo "  • Check Lambda logs: aws logs tail /aws/lambda/$LAMBDA_FUNCTION_NAME --follow"
echo "  • Test Lambda: aws lambda invoke --function-name $LAMBDA_FUNCTION_NAME --payload '{}' response.json"
echo "  • Start dashboard: cd dashboard/frontend && npm start"
echo ""
echo "📚 Documentation:"
echo "  • README.md - Complete usage guide"
echo "  • deploy/README.md - Deployment documentation"
echo ""
print_status "NL2Flow Week 3 Watchdog and Alerting System is ready!" 