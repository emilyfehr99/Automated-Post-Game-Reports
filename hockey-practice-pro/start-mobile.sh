#!/bin/bash

echo "🏒 Hockey Practice Planner - Mobile Access"
echo "=========================================="

# Kill any existing Next.js processes
echo "🔄 Stopping any existing servers..."
pkill -f 'next dev' 2>/dev/null || true
sleep 2

# Get the local IP address
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo "📱 Your computer's IP address: $LOCAL_IP"

# Start the development server with network access
echo "🚀 Starting server with mobile access..."
echo "📱 Mobile URL: http://$LOCAL_IP:3000"
echo "💻 Computer URL: http://localhost:3000"
echo ""
echo "📝 Make sure your phone is on the same WiFi network!"
echo "🔄 Press Ctrl+C to stop the server"
echo ""

npm run dev -- --hostname 0.0.0.0
