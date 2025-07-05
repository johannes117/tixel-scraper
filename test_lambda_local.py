#!/usr/bin/env python3
"""
Local testing script for the Tixel Scraper Lambda function.
This simulates the Lambda environment for local development and testing.
"""

import os
import sys
import json
from unittest.mock import Mock, patch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Mock AWS services for local testing
class MockDynamoDBTable:
    def __init__(self):
        self.data = {}
    
    def get_item(self, Key):
        item_id = Key['id']
        if item_id in self.data:
            return {'Item': self.data[item_id]}
        return {}
    
    def put_item(self, Item):
        self.data[Item['id']] = Item
        return {'ResponseMetadata': {'HTTPStatusCode': 200}}

class MockDynamoDBResource:
    def __init__(self):
        self.tables = {}
    
    def Table(self, table_name):
        if table_name not in self.tables:
            self.tables[table_name] = MockDynamoDBTable()
        return self.tables[table_name]

# Mock context object
class MockLambdaContext:
    def __init__(self):
        self.function_name = "test-tixel-scraper"
        self.function_version = "$LATEST"
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-tixel-scraper"
        self.memory_limit_in_mb = 256
        self.remaining_time_in_millis = 30000
        self.log_group_name = "/aws/lambda/test-tixel-scraper"
        self.log_stream_name = "2023/01/01/[$LATEST]abcdef123456"
        self.aws_request_id = "test-request-id"

def test_lambda_function():
    """Test the Lambda function locally"""
    
    # Set up environment variables
    os.environ['DYNAMODB_TABLE_NAME'] = 'test-notification-state'
    os.environ['RESEND_API_KEY'] = os.getenv('RESEND_API_KEY', 'test-key')
    os.environ['FROM_ADDRESS'] = os.getenv('FROM_ADDRESS', 'test@example.com')
    os.environ['TO_ADDRESSES'] = os.getenv('TO_ADDRESSES', 'recipient@example.com')
    os.environ['TIXEL_URL'] = os.getenv('TIXEL_URL', 'https://tixel.com/test')
    
    # Mock AWS services
    mock_dynamodb = MockDynamoDBResource()
    mock_context = MockLambdaContext()
    
    # Patch boto3 and resend for local testing
    with patch('boto3.resource', return_value=mock_dynamodb):
        with patch('resend.Emails.send') as mock_send_email:
            # Configure mock email response
            mock_send_email.return_value = {'id': 'test-email-id'}
            
            # Import and test the lambda function
            try:
                from lambda_function import lambda_handler
                
                # Test with empty event
                event = {}
                
                print("🧪 Testing Lambda function locally...")
                print(f"📧 From: {os.environ['FROM_ADDRESS']}")
                print(f"📧 To: {os.environ['TO_ADDRESSES']}")
                print(f"🔗 URL: {os.environ['TIXEL_URL']}")
                print("-" * 50)
                
                # Run the lambda function
                result = lambda_handler(event, mock_context)
                
                print("✅ Lambda function executed successfully!")
                print(f"📊 Result: {json.dumps(result, indent=2)}")
                
                # Check if email was called (only if tickets were found)
                if mock_send_email.called:
                    print("📧 Email notification would be sent!")
                    print(f"📧 Email call args: {mock_send_email.call_args}")
                else:
                    print("📧 No email notification (no tickets found or already notified)")
                
                return result
                
            except Exception as e:
                print(f"❌ Error testing Lambda function: {str(e)}")
                print(f"🔍 Error type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                return None

def test_with_mock_tickets():
    """Test the function with mocked ticket availability"""
    
    print("\n🎫 Testing with MOCK TICKETS AVAILABLE...")
    
    # Mock the check_tickets function to return True
    with patch('lambda_function.check_tickets', return_value=True):
        result = test_lambda_function()
        
    return result

def test_without_tickets():
    """Test the function with no tickets available"""
    
    print("\n🚫 Testing with NO TICKETS AVAILABLE...")
    
    # Mock the check_tickets function to return False
    with patch('lambda_function.check_tickets', return_value=False):
        result = test_lambda_function()
        
    return result

def main():
    """Main testing function"""
    
    print("🚀 Tixel Scraper Lambda - Local Testing")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file based on env.example")
        return
    
    # Test both scenarios
    print("\n1️⃣ Testing normal execution (real ticket check)...")
    test_lambda_function()
    
    print("\n2️⃣ Testing with mock tickets available...")
    test_with_mock_tickets()
    
    print("\n3️⃣ Testing with no tickets available...")
    test_without_tickets()
    
    print("\n✅ Local testing completed!")
    print("\n💡 Tips:")
    print("- Check the output above for any errors")
    print("- The function uses your real .env configuration")
    print("- Email sending is mocked (no actual emails sent)")
    print("- DynamoDB operations are mocked locally")

if __name__ == "__main__":
    main() 