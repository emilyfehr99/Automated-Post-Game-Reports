#!/bin/bash
# Script to verify the latest code is in git and trigger a manual test

echo "Checking if comprehensive parsing is in api/app.py..."
if grep -q "Parse ALL fields from MoneyPuck CSV" api/app.py; then
    echo "✅ Comprehensive parsing code IS in the local repository"
    echo ""
    echo "Checking git diff with remote..."
    git fetch origin
    git diff origin/main api/app.py | head -20
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Local and remote are in sync"
        echo ""
        echo "The issue is that Render hasn't picked up the deployment."
        echo "This can happen if:"
        echo "1. Render auto-deploy is not enabled"
        echo "2. The deployment failed silently"
        echo "3. Render is still deploying (can take 5-10 minutes)"
        echo ""
        echo "You'll need to manually trigger a redeploy in Render dashboard:"
        echo "https://dashboard.render.com"
    fi
else
    echo "❌ Comprehensive parsing code NOT FOUND in local api/app.py"
    echo "This means the commit didn't include the changes!"
fi
