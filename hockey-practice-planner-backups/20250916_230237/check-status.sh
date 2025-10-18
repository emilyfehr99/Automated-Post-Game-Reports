#!/bin/bash

echo "🏒 Hockey Practice Planner Status Check"
echo "========================================"

# Check if app is running
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "✅ App is RUNNING"
    echo "🌐 URL: http://localhost:3000"
    echo ""
    echo "📊 Process info:"
    ps aux | grep "next start" | grep -v grep
    echo ""
    echo "🔧 To stop: pkill -f 'next start'"
else
    echo "❌ App is NOT running"
    echo ""
    echo "🚀 To start: ./start-production.sh"
    echo "🔄 To start 24/7: ./run-forever.sh"
fi

echo ""
echo "📁 Logs: Check terminal where app was started"
echo "💾 Backup: ./backup.sh"
