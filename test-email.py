import os
from dotenv import load_dotenv
import resend

# Load environment variables from .env file
load_dotenv()

# Resend API key
resend.api_key = os.getenv('RESEND_API_KEY')

# Email parameters
from_address = os.getenv('FROM_ADDRESS')
to_addresses = os.getenv('TO_ADDRESSES').split(',')  # Assume the addresses are comma-separated in the environment variable
subject = 'Hello'
body = 'Hello World'

# Function to send email
def send_email():
    params = {
        "from": from_address,
        "to": to_addresses,
        "subject": subject,
        "html": f"<p>{body}</p>"
    }
    
    print(f"Sending email to {', '.join(to_addresses)}: {subject}\nFrom: {from_address}\n")

    try:
        email = resend.Emails.send(params)
        print(f"Email sent successfully! Email ID: {email['id']}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Send the email
send_email()