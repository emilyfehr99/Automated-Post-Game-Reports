#!/bin/bash

echo "🏒 Hockey Practice Planner - Stop Mobile Server"
echo "=============================================="

PID_FILE="hockey-mobile.pid"
LOG_FILE="hockey-mobile.log"

if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    echo "🔄 Stopping server with PID: $PID"
    
    # Kill the process
    kill $PID 2>/dev/null || true
    
    # Wait a moment and force kill if needed
    sleep 2
    kill -9 $PID 2>/dev/null || true
    
    # Clean up PID file
    rm -f $PID_FILE
    
    echo "✅ Server stopped"
else
    echo "⚠️ No PID file found. Trying to kill any Next.js processes..."
    pkill -f 'next dev' 2>/dev/null || true
    echo "✅ Any running Next.js processes killed"
fi

echo "📁 Log file preserved: $LOG_FILE"
echo "🔄 To start again: ./start-mobile-forever.sh"
