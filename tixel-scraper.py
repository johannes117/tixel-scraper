import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# SMTP credentials
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT'))
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')

# Email parameters for notification
from_address = os.getenv('FROM_ADDRESS')
to_address = os.getenv('TO_ADDRESS')
subject = 'Ticket Availability Alert'
body = 'Tickets for your event are now available! Check them out at: https://tixel.com/au/music-tickets/2024/04/20/kita-alexander-oxford-art-factor'

# Function to check ticket availability
def check_tickets():
    url = 'https://tixel.com/au/music-tickets/2024/04/20/kita-alexander-oxford-art-factor'
    headers = eval('{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}')
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Check for the specific div element indicating tickets are available
    ticket_available = soup.find_all('div', class_='space-y-3 text-left')
    return bool(ticket_available)  # Return True if tickets are available, False otherwise

# Function to send email
def send_email():
    message = MIMEMultipart()
    message['From'] = from_address
    message['To'] = to_address
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(smtp_username, smtp_password)
        text = message.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to send confirmation email
def send_confirmation_email():
    confirmation_subject = 'Subscription Confirmation'
    confirmation_body = 'You have been subscribed to the Tixel Scraper. It is now running and checking for tickets.'

    confirmation_message = MIMEMultipart()
    confirmation_message['From'] = from_address
    confirmation_message['To'] = to_address
    confirmation_message['Subject'] = confirmation_subject
    confirmation_message.attach(MIMEText(confirmation_body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(smtp_username, smtp_password)
        text = confirmation_message.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
        print("Confirmation email sent successfully!")
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")

# Main logic with adaptive checking intervals
if __name__ == '__main__':
    print("Starting ticket check...")
    email_sent = False  # Track whether an email has been sent

    # Send confirmation email
    send_confirmation_email()

    while True:
        if check_tickets():
            if not email_sent:
                print("Tickets found! Sending email...")
                send_email()
                email_sent = True
            else:
                print("Tickets are still available, no new email sent.")
            print("Waiting 10 minutes before re-checking...")
            time.sleep(600)  # Wait for 10 minutes before checking again
        else:
            if email_sent:
                print("Tickets no longer available, resuming normal checks.")
                email_sent = False  # Reset email sent status
            print("No tickets available at this time. Waiting 10 minutes before next check...")
            time.sleep(600)  # Wait for 30 seconds before checking again