#!/bin/bash

echo "🏒 Setting up Hockey Practice Planner for 24/7 production..."

# Create logs directory
mkdir -p logs

# Install PM2 globally if not already installed
if ! command -v pm2 &> /dev/null; then
    echo "📦 Installing PM2..."
    npm install -g pm2
fi

# Build the application
echo "🔨 Building application..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
    exit 1
fi

# Start with PM2
echo "🚀 Starting application with PM2..."
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on system boot
pm2 startup

echo ""
echo "🎉 Hockey Practice Planner is now running 24/7!"
echo ""
echo "📊 Useful commands:"
echo "  pm2 status          - Check app status"
echo "  pm2 logs            - View logs"
echo "  pm2 restart hockey-practice-planner - Restart app"
echo "  pm2 stop hockey-practice-planner   - Stop app"
echo "  pm2 delete hockey-practice-planner - Remove app"
echo ""
echo "🌐 Your app is running at: http://localhost:3000"
echo "📱 Access it from any device on your network!"
