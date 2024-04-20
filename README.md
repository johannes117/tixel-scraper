# Tixel Scraper

This Python script is designed to check ticket availability for a specific event on Tixel and send notifications via email and SMS when tickets become available.

## Dependencies

The script uses the following Python libraries:

- `requests`
- `beautifulsoup4`
- `smtplib`
- `email`
- `dotenv`
- `os`
- `time`
- `twilio`

## Environment Variables

The script requires the following environment variables to be set:

- `SMTP_SERVER`: The SMTP server for sending emails.
- `SMTP_PORT`: The SMTP port for sending emails.
- `SMTP_USERNAME`: The username for the SMTP server.
- `SMTP_PASSWORD`: The password for the SMTP server.
- `FROM_ADDRESS`: The email address from which the notifications will be sent.
- `TO_ADDRESSES`: The email addresses to which the notifications will be sent, separated by commas.
- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID.
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token.
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number from which the SMS notifications will be sent.
- `TO_PHONE_NUMBERS`: The phone numbers to which the SMS notifications will be sent, separated by commas.

## How to Run

1. Set the required environment variables.
2. Run the script with `python tixel-scraper.py`.

## How it Works

The script continuously checks the ticket availability for a specific event on Tixel. When tickets become available, it sends an email and an SMS notification to the specified recipients. After sending the notifications, it waits for 10 minutes before checking again. If no tickets are available, it waits for 1 minute before the next check.

## Note

This script is for educational purposes only. Please respect the terms of service of the websites you are scraping.