@echo off
echo 🎯 Polymarket AI Predictor - Windows Launcher
echo ================================================

echo.
echo Choose an option:
echo 1. Run Command Line Version
echo 2. Run Web Interface
echo 3. Run Demo
echo 4. Setup/Install Dependencies
echo 5. Exit

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Starting Command Line Version...
    python polymarket_ai_predictor.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo 🌐 Starting Web Interface...
    streamlit run polymarket_web_interface.py
) else if "%choice%"=="3" (
    echo.
    echo 🎮 Running Demo...
    python demo_polymarket_ai.py
    pause
) else if "%choice%"=="4" (
    echo.
    echo ⚙️ Running Setup...
    python setup_polymarket_ai.py
    pause
) else if "%choice%"=="5" (
    echo.
    echo 👋 Goodbye!
    exit
) else (
    echo.
    echo ❌ Invalid choice. Please run the script again.
    pause
)
