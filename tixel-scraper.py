import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time
import re
import resend
import logging
from logging.handlers import RotatingFileHandler

# Set up logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = 'tixel_scraper.log'
log_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Resend API key
resend.api_key = os.getenv('RESEND_API_KEY')

# Email parameters for notification
from_address = os.getenv('FROM_ADDRESS')
to_addresses = os.getenv('TO_ADDRESSES').split(',')
subject = 'Ticket Availability Alert'

# Tixel URL
tixel_url = os.getenv('TIXEL_URL')

# Email body for notification
body = f'General Admission Standing tickets for your event are now available! Check them out at: {tixel_url}'

def check_tickets():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(tixel_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    ticket_elements = soup.find_all('div', class_='space-y-3 text-left')
    
    # Simply check if any ticket elements exist
    return len(ticket_elements) > 0

def send_email(subject, html_file, **kwargs):
    # Read the HTML template
    with open(html_file, 'r') as file:
        html_content = file.read()
    
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
        logger.error(f"Failed to send email: {e}")

def send_confirmation():
    confirmation_subject = 'Subscription Confirmation - Tixel Scraper'
    send_email(confirmation_subject, 'subscription_confirmation_template.html')

if __name__ == '__main__':
    logger.info("Starting ticket check...")
    notification_sent = False

    # Send confirmation email
    send_confirmation()

    while True:
        try:
            if check_tickets():
                if not notification_sent:
                    logger.info("Tickets found! Sending notification...")
                    send_email('Ticket Availability Alert', 'email_template.html', tixel_url=tixel_url)
                    notification_sent = True
                else:
                    logger.info("Tickets are still available, no new notifications sent.")
                logger.info("Waiting 10 minutes before re-checking...")
                time.sleep(600)
            else:
                if notification_sent:
                    logger.info("Tickets no longer available, resuming normal checks.")
                    notification_sent = False
                logger.info("No tickets available at this time. Waiting 1 minute before next check...")
                time.sleep(60)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.info("Waiting 5 minutes before retrying...")
            time.sleep(300)