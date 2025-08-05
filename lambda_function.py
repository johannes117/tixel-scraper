import json
import boto3
import requests
from bs4 import BeautifulSoup
import os
import resend
import logging
import re

# Set up logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

# Resend API key from environment variable
resend.api_key = os.environ['RESEND_API_KEY']

# Configuration from environment variables
from_address = os.environ['FROM_ADDRESS']
to_addresses = os.environ['TO_ADDRESSES'].split(',')
tixel_url = os.environ['TIXEL_URL']
MAX_PRICE = float(os.environ.get('MAX_PRICE', 100.0))
DESIRED_QUANTITY = int(os.environ.get('DESIRED_QUANTITY', 2))

def lambda_handler(event, context):
    """
    AWS Lambda handler function that checks for ticket availability
    based on price and quantity, and sends notifications when found.
    """
    logger.info(f"Starting ticket check for {DESIRED_QUANTITY} tickets at ${MAX_PRICE} or less...")

    try:
        # Check if matching tickets are available
        found, ticket_details = check_tickets()

        # Get current notification state from DynamoDB
        notification_state = get_notification_state()

        if found:
            if not notification_state['notification_sent']:
                logger.info(f"Matching ticket found: {ticket_details}. Sending notification...")
                send_email(
                    'Matching Ticket Found!',
                    get_email_template(),
                    tixel_url=tixel_url,
                    ticket_type=ticket_details['type'],
                    ticket_price=ticket_details['price'],
                    ticket_quantity=ticket_details['quantity']
                )
                update_notification_state(True)
                logger.info("Notification sent and state updated.")
            else:
                logger.info("Matching ticket is still available, but notification was already sent. No new action taken.")
        else:
            if notification_state['notification_sent']:
                logger.info("Matching tickets no longer available. Resetting notification state to allow future alerts.")
                update_notification_state(False)
            logger.info("No tickets matching your criteria were found.")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Ticket check completed successfully.',
                'matching_ticket_found': found,
                'notification_sent_previously': notification_state['notification_sent']
            })
        }

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred during the ticket check.',
                'error': str(e)
            })
        }

def check_tickets():
    """
    Scrapes the Tixel URL for tickets matching DESIRED_QUANTITY and MAX_PRICE.

    Note: The CSS selectors used here are specific to Tixel's website structure
    as of the time of writing and may break if Tixel updates its front-end code.
    This is an inherent fragility of web scraping.

    Returns:
        tuple: (True, ticket_details_dict) if a match is found, otherwise (False, None).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(tixel_url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # This selector targets the container for ticket listings. It may need updating if Tixel changes its layout.
        ticket_listings = soup.select('div[class*="mt-6 space-y-3"] button[class*="rounded-lg"]')

        if not ticket_listings:
            logger.info("No ticket listing containers found on the page.")
            return False, None

        logger.info(f"Found {len(ticket_listings)} ticket listings to analyze.")

        for ticket in ticket_listings:
            try:
                type_element = ticket.find('p', class_='font-semibold')
                ticket_type = type_element.text.strip() if type_element else "N/A"

                details_element = ticket.find('p', class_='text-gray-500')
                if not details_element:
                    continue
                details_text = details_element.text.strip()

                price_match = re.search(r'\$(\d+\.?\d*)', details_text)
                price = float(price_match.group(1)) if price_match else -1

                quantity_match = re.search(r'(\d+)\s+ticket', details_text)
                quantity = int(quantity_match.group(1)) if quantity_match else -1

                if price > 0 and quantity > 0:
                    logger.info(f"Checking ticket: Type='{ticket_type}', Price=${price}, Quantity={quantity}")
                    # Check if it meets the user's criteria
                    if price <= MAX_PRICE and quantity == DESIRED_QUANTITY:
                        ticket_details = {
                            "type": ticket_type,
                            "price": f"{price:.2f}",
                            "quantity": quantity
                        }
                        return True, ticket_details

            except (AttributeError, ValueError, TypeError) as e:
                logger.warning(f"Could not parse a ticket listing. Error: {e}. Skipping.")
                continue

        return False, None

    except requests.RequestException as e:
        logger.error(f"Error fetching the Tixel page: {str(e)}")
        return False, None

def get_notification_state():
    """Retrieves the current notification state from DynamoDB."""
    try:
        response = table.get_item(Key={'id': 'notification_state'})
        if 'Item' in response:
            return response['Item']
        else:
            # If no state exists, create a default one.
            default_state = {'id': 'notification_state', 'notification_sent': False}
            table.put_item(Item=default_state)
            return default_state
    except Exception as e:
        logger.error(f"Error getting notification state from DynamoDB: {str(e)}")
        # Fallback to a safe default
        return {'id': 'notification_state', 'notification_sent': False}

def update_notification_state(sent_status):
    """Updates the notification state in DynamoDB."""
    try:
        table.put_item(Item={'id': 'notification_state', 'notification_sent': sent_status})
        logger.info(f"Notification state updated to: {sent_status}")
    except Exception as e:
        logger.error(f"Error updating notification state in DynamoDB: {str(e)}")

def send_email(subject, html_content, **kwargs):
    """Sends an email notification using the Resend API after replacing placeholders."""
    for key, value in kwargs.items():
        html_content = html_content.replace(f'{{{{ {key} }}}}', str(value))

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
        logger.error(f"Failed to send email via Resend: {str(e)}")
        raise

def get_email_template():
    """Reads the HTML email template from the packaged file."""
    with open('email_template.html', 'r') as file:
        return file.read()