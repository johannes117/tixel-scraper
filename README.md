# Tixel Scraper

Tixel Scraper is a Python application designed to monitor ticket availability on Tixel for specific events. It continuously checks for General Admission Standing tickets and sends email notifications when tickets become available.

## Features

- Automatic ticket checking at regular intervals
- Email notifications when tickets are available
- Fuzzy matching for various ticket type descriptions
- Logging of all activities and errors
- Headless operation on a VPS

## Requirements

- Python 3.10 or higher
- pip (Python package manager)
- A VPS or server to run the application
- Resend API key for sending emails

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/johannes117/tixel-scraper.git
   cd tixel-scraper
   ```

2. Create a virtual environment:
   ```
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root and add the following environment variables:
   ```
   RESEND_API_KEY=your_resend_api_key
   FROM_ADDRESS=your_from_email_address
   TO_ADDRESSES=recipient1@example.com,recipient2@example.com
   TIXEL_URL=https://tixel.com/your/event/url
   ```

## Usage

### Running the Application

1. Start the application:
   ```
   ./start_scraper.sh
   ```

2. Stop the application:
   ```
   ./stop_scraper.sh
   ```

### Monitoring

You can monitor the application's activity by checking the log file:
```
tail -f tixel_scraper.log
```

## Deployment

To deploy the Tixel Scraper on a VPS:

1. Connect to your VPS via SSH.
2. Clone the repository and follow the installation steps above.
3. Make the start and stop scripts executable:
   ```
   chmod +x start_scraper.sh stop_scraper.sh
   ```
4. Use the start and stop scripts to manage the application.

## File Structure

- `tixel-scraper.py`: Main application script
- `start_scraper.sh`: Script to start the application
- `stop_scraper.sh`: Script to stop the application
- `requirements.txt`: List of Python package dependencies
- `.env`: Configuration file for environment variables
- `email_template.html`: HTML template for notification emails
- `subscription_confirmation_template.html`: HTML template for subscription confirmation email

## Logging

The application logs its activity to `tixel_scraper.log`. This file uses a rotating file handler, which means it will create new log files and delete old ones to manage disk space.

## Contributing

Contributions to the Tixel Scraper project are welcome. Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is open source and available under the [MIT License](LICENSE).

## Disclaimer

This script is for educational purposes only. Please respect the terms of service of the websites you are scraping.