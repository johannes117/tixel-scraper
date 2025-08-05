#!/bin/bash

# Deployment script for the Tixel Scraper serverless application.
# This script packages the Lambda function, uploads it to a dedicated S3 bucket,
# and deploys/updates the CloudFormation stack.

set -e

# Function to load environment variables from .env file
load_env() {
    if [ -f ".env" ]; then
        echo "📄 Loading configuration from .env file..."
        export $(grep -v '^#' .env | xargs)
    else
        echo "❌ .env file not found!"
        echo "Please create a .env file from the example: cp .env.example .env"
        exit 1
    fi
}

# --- Script Start ---

# 1. Load and Validate Configuration
load_env

REQUIRED_VARS=("RESEND_API_KEY" "FROM_ADDRESS" "TO_ADDRESSES" "TIXEL_URL" "MAX_PRICE" "DESIRED_QUANTITY")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required environment variable in .env file: $var"
        exit 1
    fi
done

# Set defaults if not provided
STACK_NAME=${STACK_NAME:-"tixel-scraper"}
REGION=${AWS_REGION:-$(aws configure get region)}
if [ -z "$REGION" ]; then
    REGION="us-east-1"
    echo "⚠️ AWS region not set, defaulting to us-east-1."
fi

echo "🚀 Starting deployment of Tixel Scraper..."
echo "-------------------------------------------"
echo "📋 Stack Name:       $STACK_NAME"
echo "🌍 AWS Region:        $REGION"
echo "🔗 Tixel URL:         $TIXEL_URL"
echo "💰 Max Price:         $MAX_PRICE"
echo "🎫 Desired Quantity:  $DESIRED_QUANTITY"
echo "-------------------------------------------"

# 2. Check Prerequisites
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# 3. Package Lambda Function
TEMP_DIR=$(mktemp -d)
echo "📦 Creating deployment package in temporary directory..."
cp lambda_function.py "$TEMP_DIR/"
cp lambda_requirements.txt "$TEMP_DIR/requirements.txt"
cp email_template.html "$TEMP_DIR/"

cd "$TEMP_DIR"
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt -t . > /dev/null
zip -r ../lambda-deployment-package.zip . > /dev/null
cd - > /dev/null
echo "✅ Deployment package created: lambda-deployment-package.zip"

# 4. Upload to S3
# Use a persistent, uniquely named bucket for CloudFormation artifacts.
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
S3_BUCKET="cf-artifacts-${STACK_NAME}-${ACCOUNT_ID}-${REGION}"
LAMBDA_ZIP_KEY="lambda-deployment-package.zip"

echo "S3_BUCKET"
if ! aws s3api head-bucket --bucket "$S3_BUCKET" &>/dev/null; then
    echo "📤 S3 bucket '$S3_BUCKET' not found. Creating it..."
    aws s3 mb "s3://$S3_BUCKET" --region "$REGION"
else
    echo "✅ Using existing S3 bucket: $S3_BUCKET"
fi

echo "📤 Uploading deployment package to s3://${S3_BUCKET}/${LAMBDA_ZIP_KEY}..."
aws s3 cp lambda-deployment-package.zip "s3://${S3_BUCKET}/${LAMBDA_ZIP_KEY}"

# 5. Deploy CloudFormation Stack
echo "🏗️ Deploying CloudFormation stack... (This may take a few minutes)"
aws cloudformation deploy \
    --template-file cloudformation-template.yaml \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
        ResendApiKey="$RESEND_API_KEY" \
        FromAddress="$FROM_ADDRESS" \
        ToAddresses="$TO_ADDRESSES" \
        TixelUrl="$TIXEL_URL" \
        MaxPrice="$MAX_PRICE" \
        DesiredQuantity="$DESIRED_QUANTITY" \
        LambdaCodeS3Bucket="$S3_BUCKET" \
        LambdaCodeS3Key="$LAMBDA_ZIP_KEY" \
    --capabilities CAPABILITY_IAM \
    --region "$REGION" \
    --no-fail-on-empty-changeset

# 6. Clean up local files
echo "🧹 Cleaning up local temporary files..."
rm -rf "$TEMP_DIR"
rm lambda-deployment-package.zip

# 7. Final Output
echo "✅ Deployment completed successfully!"
echo "🎯 The scraper is now running every minute."
echo ""
echo "---"
echo "📊 Useful Commands:"
FUNCTION_NAME=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionName'].OutputValue" --output text --region "$REGION")
echo "  - View Logs:    aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
echo "  - Pause Scraper:  aws scheduler update-schedule --name ${STACK_NAME}-tixel-scraper-schedule --state DISABLED"
echo "  - Resume Scraper: aws scheduler update-schedule --name ${STACK_NAME}-tixel-scraper-schedule --state ENABLED"
echo "  - Delete Stack:   aws cloudformation delete-stack --stack-name $STACK_NAME"
echo "---"