#!/bin/bash

echo "🏒 Starting Hockey Practice Planner in production mode..."

# Check if build exists
if [ ! -d ".next" ]; then
    echo "🔨 Building application first..."
    npm run build
fi

# Start the production server
echo "🚀 Starting production server on port 3000..."
echo "🌐 Open: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm start
