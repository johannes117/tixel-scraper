#!/bin/bash

# AWS Lambda Deployment Script for Tixel Scraper
# Usage: ./deploy.sh <resend-api-key> <from-email> <to-emails> <tixel-url>

set -e

# Check if all required parameters are provided
if [ $# -ne 4 ]; then
    echo "Usage: $0 <resend-api-key> <from-email> <to-emails> <tixel-url>"
    echo "Example: $0 'your-api-key' 'from@example.com' 'to1@example.com,to2@example.com' 'https://tixel.com/your-event'"
    exit 1
fi

RESEND_API_KEY="$1"
FROM_EMAIL="$2"
TO_EMAILS="$3"
TIXEL_URL="$4"
STACK_NAME="tixel-scraper"

echo "🚀 Starting deployment of Tixel Scraper Lambda function..."

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
        FromAddress="$FROM_EMAIL" \
        ToAddresses="$TO_EMAILS" \
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

echo "✅ Deployment completed successfully!"
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
echo "🎯 The scraper is now running every 60 seconds!"
echo "You can monitor it in the AWS Console under Lambda and CloudWatch." 