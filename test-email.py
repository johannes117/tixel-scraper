import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# SMTP credentials
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT'))
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')

# Email parameters
from_address = os.getenv('FROM_ADDRESS')
to_addresses = os.getenv('TO_ADDRESSES').split(',')  # Assume the addresses are comma-separated in the environment variable
subject = 'Hello'
body = 'Hello World'

# Function to send email
def send_email():
    message = MIMEMultipart()
    message['From'] = from_address
    message['To'] = ', '.join(to_addresses)
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    print(f"Sending email to {message['To']}: {message['Subject']}\n{message['From']}\n")

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(smtp_username, smtp_password)
        text = message.as_string()
        server.sendmail(from_address, ', '.join(to_addresses), text)  # Send the email
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Send the email
send_email()