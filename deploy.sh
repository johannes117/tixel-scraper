#!/bin/bash

# AWS Lambda Deployment Script for Tixel Scraper
# Usage: ./deploy.sh [update]
# Configuration is read from .env file

set -e

# Function to load environment variables from .env file
load_env() {
    if [ -f ".env" ]; then
        echo "📄 Loading configuration from .env file..."
        export $(grep -v '^#' .env | xargs)
    else
        echo "❌ .env file not found!"
        echo "Please create a .env file based on env.example:"
        echo "  cp env.example .env"
        echo "  # Then edit .env with your actual values"
        exit 1
    fi
}

# Load environment variables
load_env

# Validate required environment variables
if [ -z "$RESEND_API_KEY" ] || [ -z "$FROM_ADDRESS" ] || [ -z "$TO_ADDRESSES" ] || [ -z "$TIXEL_URL" ]; then
    echo "❌ Missing required environment variables in .env file!"
    echo "Required variables: RESEND_API_KEY, FROM_ADDRESS, TO_ADDRESSES, TIXEL_URL"
    exit 1
fi

# Set default stack name if not provided
STACK_NAME=${STACK_NAME:-"tixel-scraper"}

# Check if this is an update operation
UPDATE_MODE=false
if [ "$1" = "update" ]; then
    UPDATE_MODE=true
    echo "🔄 Running in UPDATE mode - will update existing stack"
else
    echo "🚀 Running in DEPLOY mode - will create new stack or update if exists"
fi

echo "🚀 Starting deployment of Tixel Scraper Lambda function..."
echo "📋 Configuration:"
echo "  Stack Name: $STACK_NAME"
echo "  From Address: $FROM_ADDRESS"
echo "  To Addresses: $TO_ADDRESSES"
echo "  Tixel URL: $TIXEL_URL"
echo "  Region: $(aws configure get region)"
echo ""

# Check if stack already exists
STACK_EXISTS=false
if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &>/dev/null; then
    STACK_EXISTS=true
    echo "📦 Stack '$STACK_NAME' already exists - will update"
else
    echo "📦 Stack '$STACK_NAME' does not exist - will create new"
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI is configured"

# Create a temporary directory for packaging
TEMP_DIR=$(mktemp -d)
echo "📦 Creating deployment package in $TEMP_DIR"

# Copy Lambda function code
cp lambda_function.py "$TEMP_DIR/"
cp lambda_requirements.txt "$TEMP_DIR/requirements.txt"

# Install dependencies
echo "📥 Installing Python dependencies..."
cd "$TEMP_DIR"
pip install -r requirements.txt -t .

# Create deployment package
echo "📦 Creating deployment package..."
zip -r lambda-deployment-package.zip . -x "*.pyc" "__pycache__/*"

# Upload to S3 (create bucket if it doesn't exist)
BUCKET_NAME="tixel-scraper-lambda-$(date +%s)"
REGION=$(aws configure get region)
if [ -z "$REGION" ]; then
    REGION="us-east-1"
fi

echo "📤 Creating S3 bucket: $BUCKET_NAME"
aws s3 mb "s3://$BUCKET_NAME" --region "$REGION"

echo "📤 Uploading deployment package to S3..."
aws s3 cp lambda-deployment-package.zip "s3://$BUCKET_NAME/"

# Go back to original directory
cd - > /dev/null

# Deploy CloudFormation stack
echo "🏗️  Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file cloudformation-template.yaml \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
        ResendApiKey="$RESEND_API_KEY" \
        FromAddress="$FROM_ADDRESS" \
        ToAddresses="$TO_ADDRESSES" \
        TixelUrl="$TIXEL_URL" \
    --capabilities CAPABILITY_IAM \
    --region "$REGION"

# Update Lambda function code
echo "🔄 Updating Lambda function code..."
FUNCTION_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionName'].OutputValue" \
    --output text \
    --region "$REGION")

aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --s3-bucket "$BUCKET_NAME" \
    --s3-key "lambda-deployment-package.zip" \
    --region "$REGION"

# Clean up temporary files
echo "🧹 Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

# Clean up S3 bucket
echo "🧹 Cleaning up S3 bucket..."
aws s3 rm "s3://$BUCKET_NAME" --recursive
aws s3 rb "s3://$BUCKET_NAME"

if [ "$STACK_EXISTS" = true ]; then
    echo "✅ Stack update completed successfully!"
    echo "🔄 Configuration has been updated with your latest .env values"
else
    echo "✅ Stack deployment completed successfully!"
    echo "🎯 The scraper is now running every 60 seconds!"
fi

echo ""
echo "📊 Stack Information:"
echo "Stack Name: $STACK_NAME"
echo "Function Name: $FUNCTION_NAME"
echo "Region: $REGION"
echo ""
echo "📋 Useful Commands:"
echo "View logs: aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
echo "Test function: aws lambda invoke --function-name $FUNCTION_NAME --payload '{}' response.json"
echo "Check DynamoDB: aws dynamodb scan --table-name $STACK_NAME-notification-state"
echo ""
echo "🔧 To update configuration:"
echo "1. Edit your .env file with new values"
echo "2. Run: ./deploy.sh update"
echo ""
echo "📱 You can monitor it in the AWS Console under Lambda and CloudWatch." 