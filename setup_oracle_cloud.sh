#!/bin/bash
# Quick setup script for Oracle Cloud Free Tier
# Run this on your Oracle Cloud VM after SSH'ing in

echo "🏒 Setting up NHL Prediction Dashboard on Oracle Cloud..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python 3.12..."
sudo apt install -y python3.12 python3.12-venv python3-pip git build-essential libssl-dev libffi-dev python3-dev

# Clone repository (if not already cloned)
if [ ! -d "Automated-Post-Game-Reports" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/emilyfehr99/Automated-Post-Game-Reports.git
fi

cd Automated-Post-Game-Reports

# Create virtual environment
echo "🔧 Setting up virtual environment..."
python3.12 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service file
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/nhl-dashboard.service > /dev/null <<EOF
[Unit]
Description=NHL Prediction Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/python3 prediction_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
echo "🚀 Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable nhl-dashboard
sudo systemctl start nhl-dashboard

# Check status
echo "✅ Checking service status..."
sleep 2
sudo systemctl status nhl-dashboard --no-pager

echo ""
echo "🎉 Setup complete!"
echo "📊 Your dashboard should be running at: http://$(curl -s ifconfig.me):8080"
echo ""
echo "Useful commands:"
echo "  View logs: sudo journalctl -u nhl-dashboard -f"
echo "  Restart:   sudo systemctl restart nhl-dashboard"
echo "  Status:    sudo systemctl status nhl-dashboard"

