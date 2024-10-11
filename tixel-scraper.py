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

def fuzzy_match(text, pattern):
    # Convert both strings to lowercase for case-insensitive matching
    text = text.lower()
    pattern = pattern.lower()
    
    # Remove non-alphanumeric characters and split into words
    text_words = re.findall(r'\w+', text)
    pattern_words = re.findall(r'\w+', pattern)
    
    # Check if all pattern words are in the text words
    return all(word in text_words for word in pattern_words)

def check_tickets():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(tixel_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    ticket_elements = soup.find_all('div', class_='space-y-3 text-left')
    
    for element in ticket_elements:
        ticket_type = element.find('p', class_='font-semibold')
        if ticket_type:
            ticket_text = ticket_type.get_text(strip=True)
            if fuzzy_match(ticket_text, "GENERAL ADMISSION STANDING") or \
               fuzzy_match(ticket_text, "GA") or \
               fuzzy_match(ticket_text, "General Admission") or \
               fuzzy_match(ticket_text, "Standing"):
                return True
    
    return False

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
    logger.info("Starting ticket check for General Admission Standing...")
    notification_sent = False

    # Send confirmation email
    send_confirmation()

    while True:
        try:
            if check_tickets():
                if not notification_sent:
                    logger.info("General Admission Standing tickets found! Sending notification...")
                    send_email('Ticket Availability Alert', 'email_template.html', tixel_url=tixel_url)
                    notification_sent = True
                else:
                    logger.info("General Admission Standing tickets are still available, no new notifications sent.")
                logger.info("Waiting 10 minutes before re-checking...")
                time.sleep(600)
            else:
                if notification_sent:
                    logger.info("General Admission Standing tickets no longer available, resuming normal checks.")
                    notification_sent = False
                logger.info("No General Admission Standing tickets available at this time. Waiting 1 minute before next check...")
                time.sleep(60)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.info("Waiting 5 minutes before retrying...")
            time.sleep(300)