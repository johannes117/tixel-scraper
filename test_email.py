#!/usr/bin/env python3
"""
Standalone email test for the Tixel Scraper.
This tests the email sending functionality with REAL emails.
"""

import resend
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

def get_email_template():
    """
    Return the HTML email template as a string.
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ticket Availability Alert</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .alert {
            background-color: #e74c3c;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .test-notice {
            background-color: #f39c12;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .btn {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
        }
        .btn:hover {
            background-color: #2980b9;
        }
        .footer {
            margin-top: 20px;
            font-size: 0.8em;
            color: #7f8c8d;
            text-align: center;
        }
        .test-info {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Email Test - Ticket Availability Alert</h1>
        
        <div class="test-notice">
            This is a TEST EMAIL from your Tixel Scraper setup
        </div>
        
        <div class="alert">
            General Admission Standing tickets are now available!
        </div>
        
        <p>Great news! The tickets you've been waiting for are now available for purchase. Don't miss this opportunity to secure your spot at the event.</p>
        
        <p><strong>Ticket Type:</strong> General Admission Standing</p>
        <p><strong>Action Required:</strong> Visit the ticket sales page as soon as possible to make your purchase. Tickets may sell out quickly!</p>
        
        <a href="{{ tixel_url }}" class="btn">Buy Tickets Now</a>
        
        <div class="test-info">
            <h3>📊 Test Information</h3>
            <p><strong>Test Time:</strong> {{ test_time }}</p>
            <p><strong>From Address:</strong> {{ from_address }}</p>
            <p><strong>To Address:</strong> {{ to_addresses }}</p>
            <p><strong>Tixel URL:</strong> {{ tixel_url }}</p>
        </div>
        
        <p class="footer">
            This is a TEST message from the Tixel Scraper email system. 
            If you received this, your email configuration is working correctly! 🎉
        </p>
    </div>
</body>
</html>"""

def send_test_email():
    """
    Send a test email using the actual Resend API.
    """
    # Get configuration from environment variables
    resend_api_key = os.getenv('RESEND_API_KEY')
    from_address = os.getenv('FROM_ADDRESS')
    to_addresses = os.getenv('TO_ADDRESSES', '').split(',')
    tixel_url = os.getenv('TIXEL_URL', 'https://tixel.com/test')
    
    # Validate configuration
    if not resend_api_key:
        print("❌ RESEND_API_KEY not found in .env file!")
        return False
    
    if not from_address:
        print("❌ FROM_ADDRESS not found in .env file!")
        return False
    
    if not to_addresses or not to_addresses[0]:
        print("❌ TO_ADDRESSES not found in .env file!")
        return False
    
    # Set up Resend API
    resend.api_key = resend_api_key
    
    # Get email template and replace placeholders
    html_content = get_email_template()
    
    # Replace placeholders
    html_content = html_content.replace('{{ tixel_url }}', tixel_url)
    html_content = html_content.replace('{{ test_time }}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    html_content = html_content.replace('{{ from_address }}', from_address)
    html_content = html_content.replace('{{ to_addresses }}', ', '.join(to_addresses))
    
    # Prepare email parameters
    params = {
        "from": from_address,
        "to": [addr.strip() for addr in to_addresses],  # Clean up addresses
        "subject": "🧪 TEST: Tixel Scraper Email Configuration",
        "html": html_content
    }
    
    print(f"📧 Sending test email...")
    print(f"  From: {from_address}")
    print(f"  To: {', '.join(params['to'])}")
    print(f"  Subject: {params['subject']}")
    
    try:
        # Send the email
        response = resend.Emails.send(params)
        
        print(f"✅ Email sent successfully!")
        print(f"📧 Email ID: {response['id']}")
        print(f"🔗 Tixel URL in email: {tixel_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Provide helpful troubleshooting tips
        print("\n💡 Troubleshooting Tips:")
        print("  1. Check your RESEND_API_KEY is correct")
        print("  2. Verify your FROM_ADDRESS is verified in Resend")
        print("  3. Check your TO_ADDRESSES format (comma-separated)")
        print("  4. Ensure your Resend account has sending permissions")
        
        return False

def validate_configuration():
    """
    Validate the email configuration before sending.
    """
    print("🔍 Validating email configuration...")
    
    config = {
        'RESEND_API_KEY': os.getenv('RESEND_API_KEY'),
        'FROM_ADDRESS': os.getenv('FROM_ADDRESS'),
        'TO_ADDRESSES': os.getenv('TO_ADDRESSES'),
        'TIXEL_URL': os.getenv('TIXEL_URL')
    }
    
    all_valid = True
    
    for key, value in config.items():
        if value:
            if key == 'RESEND_API_KEY':
                display_value = f"{value[:8]}..." if len(value) > 8 else value
            else:
                display_value = value
            print(f"  ✅ {key}: {display_value}")
        else:
            print(f"  ❌ {key}: Not set")
            all_valid = False
    
    if all_valid:
        print("✅ All configuration values are present!")
    else:
        print("❌ Some configuration values are missing!")
    
    return all_valid

def main():
    """Main testing function"""
    
    print("📧 Tixel Scraper Email Test")
    print("=" * 40)
    print("⚠️  WARNING: This will send a REAL email!")
    print("=" * 40)
    
    # Validate configuration
    if not validate_configuration():
        print("\n❌ Configuration validation failed!")
        print("Please check your .env file and ensure all required variables are set.")
        return
    
    # Ask for confirmation
    print(f"\n🤔 Are you sure you want to send a test email?")
    print("This will use your actual Resend API key and send to your configured addresses.")
    
    try:
        confirmation = input("Type 'yes' to continue: ").lower().strip()
        if confirmation != 'yes':
            print("❌ Test cancelled.")
            return
    except KeyboardInterrupt:
        print("\n❌ Test cancelled.")
        return
    
    # Send test email
    print(f"\n📤 Sending test email...")
    success = send_test_email()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 EMAIL TEST SUCCESSFUL!")
        print("✅ Check your inbox for the test email")
        print("✅ Your email configuration is working correctly")
        print("✅ You're ready to deploy the Lambda function")
    else:
        print("❌ EMAIL TEST FAILED!")
        print("🔧 Please fix the configuration issues above")
        print("🔧 Then try running the test again")

if __name__ == "__main__":
    main() 