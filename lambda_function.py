import json
import boto3
import requests
from bs4 import BeautifulSoup
import os
import resend
import logging

# Set up logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

# Resend API key from environment variable
resend.api_key = os.environ['RESEND_API_KEY']

# Email parameters from environment variables
from_address = os.environ['FROM_ADDRESS']
to_addresses = os.environ['TO_ADDRESSES'].split(',')
tixel_url = os.environ['TIXEL_URL']

def lambda_handler(event, context):
    """
    AWS Lambda handler function that checks for ticket availability
    and sends notifications when tickets are found.
    """
    logger.info("Starting ticket check...")
    
    try:
        # Check if tickets are available
        tickets_available = check_tickets()
        
        # Get current notification state from DynamoDB
        notification_state = get_notification_state()
        
        if tickets_available:
            if not notification_state['notification_sent']:
                logger.info("Tickets found! Sending notification...")
                send_email('Ticket Availability Alert', get_email_template(), tixel_url=tixel_url)
                update_notification_state(True)
                logger.info("Notification sent and state updated.")
            else:
                logger.info("Tickets are still available, no new notifications sent.")
        else:
            if notification_state['notification_sent']:
                logger.info("Tickets no longer available, resetting notification state.")
                update_notification_state(False)
            logger.info("No tickets available at this time.")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Ticket check completed successfully',
                'tickets_available': tickets_available,
                'notification_sent': notification_state['notification_sent']
            })
        }
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error occurred during ticket check',
                'error': str(e)
            })
        }

def check_tickets():
    """
    Check if tickets are available on the Tixel page.
    Returns True if tickets are found, False otherwise.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    try:
        response = requests.get(tixel_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        ticket_elements = soup.find_all('div', class_='space-y-3 text-left')
        
        # Simply check if any ticket elements exist
        return len(ticket_elements) > 0
        
    except requests.RequestException as e:
        logger.error(f"Error fetching Tixel page: {str(e)}")
        return False

def get_notification_state():
    """
    Get the current notification state from DynamoDB.
    Returns a dictionary with notification_sent boolean.
    """
    try:
        response = table.get_item(Key={'id': 'notification_state'})
        if 'Item' in response:
            return response['Item']
        else:
            # If no item exists, create default state
            default_state = {'id': 'notification_state', 'notification_sent': False}
            table.put_item(Item=default_state)
            return default_state
    except Exception as e:
        logger.error(f"Error getting notification state: {str(e)}")
        return {'id': 'notification_state', 'notification_sent': False}

def update_notification_state(notification_sent):
    """
    Update the notification state in DynamoDB.
    """
    try:
        table.put_item(Item={
            'id': 'notification_state',
            'notification_sent': notification_sent
        })
        logger.info(f"Notification state updated to: {notification_sent}")
    except Exception as e:
        logger.error(f"Error updating notification state: {str(e)}")

def send_email(subject, html_content, **kwargs):
    """
    Send email notification using Resend API.
    """
    # Replace any placeholders in the template
    for key, value in kwargs.items():
        html_content = html_content.replace(f'{{{{ {key} }}}}', value)
    
    params = {
        "from": from_address,
        "to": to_addresses,
        "subject": subject,
        "html": html_content
    }
    
    try:
        email = resend.Emails.send(params)
        logger.info(f"Email sent successfully! Email ID: {email['id']}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise

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
    </style>
</head>
<body>
    <div class="container">
        <h1>Ticket Availability Alert</h1>
        <div class="alert">
            General Admission Standing tickets are now available!
        </div>
        <p>Great news! The tickets you've been waiting for are now available for purchase. Don't miss this opportunity to secure your spot at the event.</p>
        <p><strong>Ticket Type:</strong> General Admission Standing</p>
        <p><strong>Action Required:</strong> Visit the ticket sales page as soon as possible to make your purchase. Tickets may sell out quickly!</p>
        <a href="{{ tixel_url }}" class="btn">Buy Tickets Now</a>
        <p class="footer">This is an automated message from the Tixel Scraper. If you no longer wish to receive these alerts, please update your notification settings.</p>
    </div>
</body>
</html>""" 