#!/bin/bash

echo "🎯 Polymarket AI Predictor - Launcher"
echo "================================================"

echo ""
echo "Choose an option:"
echo "1. Run Command Line Version"
echo "2. Run Web Interface"
echo "3. Run Demo"
echo "4. Setup/Install Dependencies"
echo "5. Exit"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting Command Line Version..."
        python3 polymarket_ai_predictor.py
        ;;
    2)
        echo ""
        echo "🌐 Starting Web Interface..."
        streamlit run polymarket_web_interface.py
        ;;
    3)
        echo ""
        echo "🎮 Running Demo..."
        python3 demo_polymarket_ai.py
        ;;
    4)
        echo ""
        echo "⚙️ Running Setup..."
        python3 setup_polymarket_ai.py
        ;;
    5)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
