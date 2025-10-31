#!/usr/bin/env python3
"""
Tixel Ticket Scraper - Long Running Script
A Python script that monitors Tixel for ticket availability and sends email notifications.
"""

import json
import requests
from bs4 import BeautifulSoup
import os
import resend
import logging
from logging.handlers import RotatingFileHandler
import re
import time
import yaml
import signal
import sys
from pathlib import Path

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_flag
    logger.info("Shutdown signal received. Finishing current check and exiting...")
    shutdown_flag = True

def load_config(config_path='config.yaml'):
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Please create a config.yaml file. See config.yaml for an example."
        )

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config

def setup_logging(log_file, log_level):
    """Configure logging to both file and console"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers
    logger.handlers = []

    # File handler with rotation (max 10MB, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def load_notification_state(state_file='state.json'):
    """Load notification state from JSON file"""
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Could not parse {state_file}, creating new state")

    # Default state
    return {'notification_sent': False}

def save_notification_state(state, state_file='state.json'):
    """Save notification state to JSON file"""
    try:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        logger.debug(f"State saved: {state}")
    except Exception as e:
        logger.error(f"Error saving state to {state_file}: {str(e)}")

def check_tickets(tixel_url, max_price, desired_quantity):
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
                    if price <= max_price and quantity == desired_quantity:
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

def send_email(subject, html_content, from_address, to_addresses, **kwargs):
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
    """Reads the HTML email template"""
    # Try multiple possible locations for the template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        'email_template.html',
        os.path.join(script_dir, 'email_template.html'),
    ]

    for template_path in possible_paths:
        if os.path.exists(template_path):
            with open(template_path, 'r') as file:
                return file.read()

    # If no template found, use a simple default
    logger.warning("Email template not found, using default template")
    return """
    <html>
        <body>
            <h1>Matching Ticket Found!</h1>
            <p><strong>Type:</strong> {{ ticket_type }}</p>
            <p><strong>Price:</strong> ${{ ticket_price }}</p>
            <p><strong>Quantity:</strong> {{ ticket_quantity }}</p>
            <p><a href="{{ tixel_url }}">View tickets on Tixel</a></p>
        </body>
    </html>
    """

def run_check_cycle(config, state_file='state.json'):
    """Run one complete check cycle"""
    # Extract config values
    tixel_url = config['scraper']['tixel_url']
    max_price = config['scraper']['max_price']
    desired_quantity = config['scraper']['desired_quantity']
    from_address = config['email']['from_address']
    to_addresses = config['email']['to_addresses']

    logger.info(f"Starting ticket check for {desired_quantity} tickets at ${max_price} or less...")

    try:
        # Check if matching tickets are available
        found, ticket_details = check_tickets(tixel_url, max_price, desired_quantity)

        # Get current notification state
        notification_state = load_notification_state(state_file)

        if found:
            if not notification_state.get('notification_sent', False):
                logger.info(f"Matching ticket found: {ticket_details}. Sending notification...")
                send_email(
                    'Matching Ticket Found!',
                    get_email_template(),
                    from_address,
                    to_addresses,
                    tixel_url=tixel_url,
                    ticket_type=ticket_details['type'],
                    ticket_price=ticket_details['price'],
                    ticket_quantity=ticket_details['quantity']
                )
                notification_state['notification_sent'] = True
                save_notification_state(notification_state, state_file)
                logger.info("Notification sent and state updated.")
            else:
                logger.info("Matching ticket is still available, but notification was already sent. No new action taken.")
        else:
            if notification_state.get('notification_sent', False):
                logger.info("Matching tickets no longer available. Resetting notification state to allow future alerts.")
                notification_state['notification_sent'] = False
                save_notification_state(notification_state, state_file)
            logger.info("No tickets matching your criteria were found.")

    except Exception as e:
        logger.error(f"An error occurred during check cycle: {str(e)}", exc_info=True)

def main():
    """Main function to run the scraper continuously"""
    global logger, shutdown_flag

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Setup logging
    logger = setup_logging(
        config['logging']['log_file'],
        config['logging']['log_level']
    )

    # Set Resend API key
    resend.api_key = config['email']['resend_api_key']

    # Get poll interval
    poll_interval = config['scraper']['poll_interval']

    logger.info("="*60)
    logger.info("Tixel Scraper Started")
    logger.info("="*60)
    logger.info(f"Target URL: {config['scraper']['tixel_url']}")
    logger.info(f"Max Price: ${config['scraper']['max_price']}")
    logger.info(f"Desired Quantity: {config['scraper']['desired_quantity']}")
    logger.info(f"Poll Interval: {poll_interval} seconds")
    logger.info(f"Log File: {config['logging']['log_file']}")
    logger.info("="*60)
    logger.info("Press Ctrl+C to stop")
    logger.info("")

    # Main loop
    while not shutdown_flag:
        try:
            run_check_cycle(config)

            # Wait for next cycle (or until shutdown signal)
            if not shutdown_flag:
                logger.info(f"Waiting {poll_interval} seconds until next check...")
                time.sleep(poll_interval)

        except Exception as e:
            logger.error(f"Unexpected error in main loop: {str(e)}", exc_info=True)
            if not shutdown_flag:
                logger.info(f"Waiting {poll_interval} seconds before retry...")
                time.sleep(poll_interval)

    logger.info("="*60)
    logger.info("Tixel Scraper Stopped")
    logger.info("="*60)

if __name__ == "__main__":
    main()
