# Free Hosting Guide - Oracle Cloud Always-Free Tier

Oracle Cloud offers a **truly free forever** VPS that you can use to host your Flask app 24/7!

## Why Oracle Cloud Free Tier?

- ✅ **100% FREE forever** (not a trial, not a credit)
- ✅ **Always-on VPS** - Your app runs 24/7
- ✅ **Fast performance** - Much faster than Render's free tier
- ✅ **2 Always-Free VMs** (AMD) or **4 Always-Free VMs** (ARM)
- ✅ **10TB data transfer per month**
- ✅ **No credit card required** (for free tier)

## Step-by-Step Setup

### 1. Sign Up for Oracle Cloud

1. Go to https://www.oracle.com/cloud/free/
2. Click "Start for Free"
3. Sign up (you'll need an email and phone number)
4. **No credit card required** for the free tier!

### 2. Create a Free VM Instance

1. Once logged in, go to **Compute** → **Instances**
2. Click **Create Instance**
3. Configure:
   - **Name**: `nhl-dashboard` (or whatever you want)
   - **Image**: Choose **Ubuntu 22.04** (or latest)
   - **Shape**: Select **VM.Standard.A1.Flex** (ARM - 4 cores, 24GB RAM FREE)
     - OR **VM.Standard.E2.1.Micro** (AMD - 1 core, 1GB RAM FREE)
   - **Networking**: Use default VCN
   - **SSH Keys**: Generate a new key pair or upload your existing one
4. Click **Create**

### 3. Set Up Security Rules (Allow HTTP/HTTPS)

1. Go to **Networking** → **Virtual Cloud Networks**
2. Click on your VCN
3. Go to **Security Lists** → **Default Security List**
4. Click **Add Ingress Rules**:
   - **Source Type**: CIDR
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: TCP
   - **Destination Port Range**: `8080` (or your app's port)
   - Click **Add Ingress Rules**
5. Repeat for port `80` and `443` if you want to set up a reverse proxy later

### 4. Connect to Your VM

```bash
# SSH into your VM (use the public IP from the instance page)
ssh -i ~/.ssh/your-key ubuntu@YOUR_PUBLIC_IP
```

### 5. Install Dependencies on the VM

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12 and pip
sudo apt install -y python3.12 python3.12-venv python3-pip git

# Install system dependencies (for your Python packages)
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
```

### 6. Clone Your Repository

```bash
# Clone your repo
git clone https://github.com/emilyfehr99/Automated-Post-Game-Reports.git
cd Automated-Post-Game-Reports

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 7. Set Up the App to Run 24/7

We'll use `systemd` to keep your app running:

```bash
# Create a systemd service file
sudo nano /etc/systemd/system/nhl-dashboard.service
```

Paste this content:

```ini
[Unit]
Description=NHL Prediction Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Automated-Post-Game-Reports
Environment="PATH=/home/ubuntu/Automated-Post-Game-Reports/venv/bin"
ExecStart=/home/ubuntu/Automated-Post-Game-Reports/venv/bin/python3 prediction_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save and exit (Ctrl+X, then Y, then Enter)

### 8. Start the Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start the service
sudo systemctl start nhl-dashboard

# Enable it to start on boot
sudo systemctl enable nhl-dashboard

# Check status
sudo systemctl status nhl-dashboard
```

### 9. Access Your App

Your app will be available at: `http://YOUR_PUBLIC_IP:8080`

You can check your VM's public IP in the Oracle Cloud console under **Compute** → **Instances**.

### 10. (Optional) Set Up a Domain Name

If you want a custom domain:
1. Get a free domain from Freenom or use a subdomain from a free DNS service
2. Point it to your Oracle Cloud public IP
3. Set up nginx as a reverse proxy (optional, for port 80/443)

## Maintenance Commands

```bash
# View logs
sudo journalctl -u nhl-dashboard -f

# Restart the app
sudo systemctl restart nhl-dashboard

# Stop the app
sudo systemctl stop nhl-dashboard

# Update your code
cd ~/Automated-Post-Game-Reports
git pull
sudo systemctl restart nhl-dashboard
```

## Alternative: Fly.io (Also Free)

If you prefer a simpler PaaS option:

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Sign up: `fly auth signup`
3. Deploy: `fly launch` (in your project directory)
4. Free tier includes 3 shared VMs

## Why This is Better Than Render

- ✅ **Always-on** - No cold starts
- ✅ **Faster** - Real VPS performance
- ✅ **More control** - You own the server
- ✅ **Truly free** - No time limits or credit requirements
- ✅ **Better for Flask** - No serverless limitations

Your app will be fast and always available!

