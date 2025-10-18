#!/bin/bash

echo "🏒 Hockey Practice Planner - Mobile Status Check"
echo "=============================================="

PID_FILE="hockey-mobile.pid"
LOG_FILE="hockey-mobile.log"

# Get the local IP address
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')

if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    
    # Check if process is running
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Server is RUNNING (PID: $PID)"
        echo "📱 Mobile URL: http://$LOCAL_IP:3000"
        echo "💻 Computer URL: http://localhost:3000"
        echo ""
        
        # Test if server is responding
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
            echo "🌐 Server is responding to requests"
        else
            echo "⚠️ Server process running but not responding"
        fi
        
        echo "📁 Log file: $LOG_FILE"
        echo "🛑 To stop: ./stop-mobile.sh"
    else
        echo "❌ Server is NOT running (PID file exists but process not found)"
        echo "🧹 Cleaning up PID file..."
        rm -f $PID_FILE
        echo "🔄 To start: ./start-mobile-forever.sh"
    fi
else
    echo "❌ Server is NOT running (no PID file)"
    echo "🔄 To start: ./start-mobile-forever.sh"
fi
