#!/bin/bash

echo "🏒 Starting Hockey Practice Planner..."

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2 not found. Please run ./setup-production.sh first"
    exit 1
fi

# Check if app is already running
if pm2 list | grep -q "hockey-practice-planner"; then
    echo "🔄 App is already running. Restarting..."
    pm2 restart hockey-practice-planner
else
    echo "🚀 Starting app..."
    pm2 start ecosystem.config.js
fi

echo ""
echo "✅ Hockey Practice Planner is running!"
echo "🌐 Open: http://localhost:3000"
echo ""
echo "📊 Commands:"
echo "  pm2 status    - Check status"
echo "  pm2 logs      - View logs"
echo "  pm2 stop      - Stop app"
