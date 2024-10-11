import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import time
from twilio.rest import Client
import re

# Load environment variables from .env file
load_dotenv()

# SMTP credentials
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT'))
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')

# Email parameters for notification
from_address = os.getenv('FROM_ADDRESS')
to_addresses = os.getenv('TO_ADDRESSES').split(',')
subject = 'Ticket Availability Alert'

# Tixel URL
tixel_url = os.getenv('TIXEL_URL')

# Email parameters for notification
body = f'General Admission Standing tickets for your event are now available! Check them out at: {tixel_url}'

# Twilio credentials
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
to_phone_numbers = os.getenv('TO_PHONE_NUMBERS').split(',')

def fuzzy_match(text, pattern):
    # Convert both to lowercase for case-insensitive matching
    text = text.lower()
    pattern = pattern.lower()
    
    # Create a regex pattern for fuzzy matching
    regex_pattern = r'\b(' + '|'.join(re.escape(word) for word in pattern.split()) + r')\b'
    
    # Count the number of words that match
    matches = re.findall(regex_pattern, text)
    
    # If more than half of the words match, consider it a match
    return len(matches) >= len(pattern.split()) / 2

# Function to check ticket availability
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

# Function to send email
def send_email():
    message = MIMEMultipart()
    message['From'] = from_address
    message['To'] = ', '.join(to_addresses)
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = message.as_string()
        server.sendmail(from_address, ', '.join(to_addresses), text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to send SMS
def send_sms():
    client = Client(twilio_account_sid, twilio_auth_token)
    for phone_number in to_phone_numbers:
        message = client.messages.create(
            body=f'General Admission Standing tickets for your event are now available! Check them out at: {tixel_url}',
            from_=twilio_phone_number,
            to=phone_number.strip()
        )
        print(f"SMS sent successfully to {phone_number}! Message SID: {message.sid}")

# Function to send confirmation email and SMS
def send_confirmation():
    confirmation_subject = 'Subscription Confirmation'
    confirmation_body = 'You have been subscribed to the Tixel Scraper. It is now running and checking for General Admission Standing tickets.'

    # Send confirmation email
    confirmation_message = MIMEMultipart()
    confirmation_message['From'] = from_address
    confirmation_message['To'] = ', '.join(to_addresses)
    confirmation_message['Subject'] = confirmation_subject
    confirmation_message.attach(MIMEText(confirmation_body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = confirmation_message.as_string()
        server.sendmail(from_address, ', '.join(to_addresses), text)
        server.quit()
        print("Confirmation email sent successfully!")
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")

    # Send confirmation SMS
    client = Client(twilio_account_sid, twilio_auth_token)
    for phone_number in to_phone_numbers:
        message = client.messages.create(
            body='You have been subscribed to the Tixel Scraper. It is now running and checking for General Admission Standing tickets.',
            from_=twilio_phone_number,
            to=phone_number.strip()
        )
        print(f"Confirmation SMS sent successfully to {phone_number}! Message SID: {message.sid}")

# Main logic with adaptive checking intervals
if __name__ == '__main__':
    print("Starting ticket check for General Admission Standing...")
    notification_sent = False

    # Send confirmation email and SMS
    send_confirmation()

    while True:
        if check_tickets():
            if not notification_sent:
                print("General Admission Standing tickets found! Sending notifications...")
                send_email()
                send_sms()
                notification_sent = True
            else:
                print("General Admission Standing tickets are still available, no new notifications sent.")
            print("Waiting 10 minutes before re-checking...")
            time.sleep(600)
        else:
            if notification_sent:
                print("General Admission Standing tickets no longer available, resuming normal checks.")
                notification_sent = False
            print("No General Admission Standing tickets available at this time. Waiting 1 minute before next check...")
            time.sleep(60)