#!/bin/bash

# Navigate to the script directory
cd /root/tixel-scraper

# Activate the virtual environment
source venv/bin/activate

# Start the script using nohup
nohup python3 tixel-scraper.py > /dev/null 2>&1 &

# Save the PID to a file
echo $! > scraper.pid

echo "Tixel scraper started. PID: $(cat scraper.pid)"