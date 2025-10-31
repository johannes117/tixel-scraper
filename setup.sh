#!/bin/bash

# Setup script for Tixel Scraper on Ubuntu VPS
# Run this script after cloning the repository to your VPS

set -e

echo "======================================"
echo "Tixel Scraper Setup for Ubuntu VPS"
echo "======================================"
echo ""

# Get current user and directory
CURRENT_USER=$(whoami)
INSTALL_DIR=$(pwd)

echo "Installing as user: $CURRENT_USER"
echo "Installation directory: $INSTALL_DIR"
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo "Warning: This script is designed for Ubuntu/Debian systems."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install Python 3 and pip if not present
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
else
    echo "Python 3 is already installed: $(python3 --version)"
fi
echo ""

# Create virtual environment
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing and recreating..."
    rm -rf venv
fi
python3 -m venv venv
echo ""

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ".env file created. IMPORTANT: Edit it with your Resend API key before starting the scraper."
    echo "  nano .env"
else
    echo ".env file already exists. Skipping creation."
fi
echo ""

# Config.yaml should already exist in the repo, but check anyway
if [ ! -f "config.yaml" ]; then
    echo "WARNING: config.yaml not found! This file should be in the repository."
    echo "Please ensure config.yaml exists before running the scraper."
else
    echo "config.yaml found. You can edit it to customize your settings:"
    echo "  nano config.yaml"
fi
echo ""

# Setup systemd service
echo "Setting up systemd service..."

# Create service file with correct paths
SERVICE_FILE="tixel-scraper.service"
TEMP_SERVICE="/tmp/tixel-scraper.service.tmp"

cat > "$TEMP_SERVICE" << EOF
[Unit]
Description=Tixel Ticket Scraper
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/main.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=tixel-scraper

[Install]
WantedBy=multi-user.target
EOF

# Copy to systemd directory
sudo cp "$TEMP_SERVICE" /etc/systemd/system/tixel-scraper.service
sudo chmod 644 /etc/systemd/system/tixel-scraper.service
sudo systemctl daemon-reload

echo "Systemd service installed."
echo ""

# Make main.py executable
chmod +x main.py

echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env with your Resend API key:"
echo "   nano .env"
echo ""
echo "2. Edit config.yaml with your settings (URL, price, quantity, etc):"
echo "   nano config.yaml"
echo ""
echo "3. Test the scraper manually:"
echo "   ./main.py"
echo "   (Press Ctrl+C to stop)"
echo ""
echo "4. Once working, enable and start the service:"
echo "   sudo systemctl enable tixel-scraper"
echo "   sudo systemctl start tixel-scraper"
echo ""
echo "Useful commands:"
echo "  - View logs:        sudo journalctl -u tixel-scraper -f"
echo "  - Check status:     sudo systemctl status tixel-scraper"
echo "  - Stop service:     sudo systemctl stop tixel-scraper"
echo "  - Restart service:  sudo systemctl restart tixel-scraper"
echo "  - Disable service:  sudo systemctl disable tixel-scraper"
echo ""
echo "The scraper will also create a local log file: tixel-scraper.log"
echo "You can tail it with: tail -f tixel-scraper.log"
echo ""
