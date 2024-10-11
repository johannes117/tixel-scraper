#!/bin/bash

# Navigate to the script directory
cd /root/tixel-scraper

# Check if PID file exists
if [ -f scraper.pid ]; then
    PID=$(cat scraper.pid)
    
    # Check if the process is running
    if ps -p $PID > /dev/null; then
        echo "Stopping Tixel scraper (PID: $PID)..."
        kill $PID
        rm scraper.pid
        echo "Tixel scraper stopped."
    else
        echo "Tixel scraper is not running."
        rm scraper.pid
    fi
else
    echo "PID file not found. Tixel scraper may not be running."
fi