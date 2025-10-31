# Tixel Ticket Scraper

A Python-based ticket monitoring application that automatically checks Tixel for ticket availability and sends email notifications when tickets matching your criteria (price and quantity) become available.

## Features

- **Continuous Monitoring**: Long-running script that checks Tixel at configurable intervals
- **Criteria-Based Filtering**: Finds tickets based on your desired quantity and maximum price
- **Smart Notifications**: Remembers when a notification has been sent to avoid spam
- **Easy Configuration**: Simple YAML configuration file for all settings
- **Robust Logging**: Rotating log files with configurable log levels
- **Systemd Integration**: Run as a background service on Ubuntu with automatic restart
- **Graceful Shutdown**: Properly handles stop signals for clean exits

## Prerequisites

- Ubuntu VPS (or any Linux system with systemd)
- Python 3.9 or higher
- A Resend API Key for sending email notifications (get one from [resend.com](https://resend.com))
- Git installed on your VPS

## Quick Start

### 1. Clone the Repository

SSH into your VPS and clone the repository:

```bash
git clone https://github.com/your-username/tixel-scraper.git
cd tixel-scraper
```

### 2. Run the Setup Script

The setup script will install dependencies, create a virtual environment, and set up the systemd service:

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure the Scraper

Edit the `config.yaml` file with your settings:

```bash
nano config.yaml
```

Update the following values:

```yaml
email:
  resend_api_key: "your-resend-api-key-here"
  from_address: "notifications@yourdomain.com"
  to_addresses:
    - "your-email@example.com"

scraper:
  tixel_url: "https://tixel.com/au/music-tickets/your-event"
  max_price: 150.0
  desired_quantity: 2
  poll_interval: 60  # seconds between checks

logging:
  log_file: "tixel-scraper.log"
  log_level: "INFO"
```

### 4. Test the Scraper

Before running as a service, test it manually:

```bash
./main.py
```

Press `Ctrl+C` to stop. Check that it's working correctly by monitoring the output.

### 5. Enable and Start the Service

Once you've confirmed it works, enable and start the systemd service:

```bash
sudo systemctl enable tixel-scraper
sudo systemctl start tixel-scraper
```

## Managing the Scraper

### View Logs

View live logs from the service:

```bash
sudo journalctl -u tixel-scraper -f
```

Or tail the local log file:

```bash
tail -f tixel-scraper.log
```

### Check Status

```bash
sudo systemctl status tixel-scraper
```

### Stop the Scraper

```bash
sudo systemctl stop tixel-scraper
```

### Restart the Scraper

After changing configuration, restart the service:

```bash
sudo systemctl restart tixel-scraper
```

### Disable Auto-Start

```bash
sudo systemctl disable tixel-scraper
```

## Configuration Options

### Email Settings

- `resend_api_key`: Your Resend API key
- `from_address`: Email address to send notifications from (must be verified in Resend)
- `to_addresses`: List of email addresses to receive notifications

### Scraper Settings

- `tixel_url`: The Tixel event page to monitor
- `max_price`: Maximum price per ticket you're willing to pay
- `desired_quantity`: Exact number of tickets you want
- `poll_interval`: How often to check for tickets (in seconds)

### Logging Settings

- `log_file`: Path to the log file
- `log_level`: Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## How It Works

1. **Monitoring**: The script continuously polls the Tixel URL at your specified interval
2. **Matching**: When tickets are found, it checks if they match your price and quantity criteria
3. **State Management**: A local `state.json` file tracks whether a notification has been sent
4. **Notification**: When matching tickets are found for the first time, an email is sent
5. **Reset**: When tickets disappear, the state resets so you'll be notified of new matches

## Project Structure

```
.
├── main.py                    # Main application script
├── config.yaml                # Configuration file
├── email_template.html        # Email notification template
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup script for VPS
├── tixel-scraper.service      # Systemd service file template
├── state.json                 # Notification state (auto-generated)
├── tixel-scraper.log          # Log file (auto-generated)
└── README.md                  # This file
```

## Troubleshooting

### Scraper Won't Start

Check the logs for errors:

```bash
sudo journalctl -u tixel-scraper -n 50
```

Common issues:
- Invalid `config.yaml` syntax
- Missing or incorrect Resend API key
- Python dependencies not installed correctly

### No Emails Being Sent

1. Verify your Resend API key is correct
2. Ensure the `from_address` is verified in your Resend account
3. Check the logs for email sending errors
4. Verify the scraper is finding tickets (check logs)

### High CPU Usage

Increase the `poll_interval` in `config.yaml` to reduce check frequency.

### Permission Errors

Ensure the service is running as the correct user and has permissions to write to the log file and state file.

## Updating the Scraper

To update to the latest version:

```bash
cd ~/tixel-scraper
sudo systemctl stop tixel-scraper
git pull
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl start tixel-scraper
```

## Security Considerations

- **Configuration Security**: Keep your `config.yaml` file secure as it contains your API key
- **HTTPS**: The scraper uses HTTPS for all web requests
- **Rate Limiting**: Be respectful of Tixel's servers by not setting too aggressive a poll interval
- **Firewall**: Consider restricting outbound connections to only necessary domains

## Disclaimer

This script is for personal, educational purposes only. Web scraping may be against the terms of service of some websites. Please ensure you are not violating Tixel's Terms of Service. The creators of this script are not responsible for any misuse.

## License

MIT License - feel free to use and modify as needed.
