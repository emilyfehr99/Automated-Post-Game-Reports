#!/bin/bash

echo "🏒 NHL Post-Game Report Generator Setup 🏒"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version detected. Python $required_version+ is required."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing required packages..."
pip install -r requirements.txt

# Create outputs directory
echo "📁 Creating outputs directory..."
mkdir -p outputs

# Test the installation
echo "🧪 Testing installation..."
python3 -c "
try:
    import requests
    import pandas
    import matplotlib
    import seaborn
    import reportlab
    from PIL import Image
    import numpy
    print('✅ All packages imported successfully!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "To use the application:"
    echo "1. Activate the virtual environment: source venv/bin/activate"
    echo "2. Run the generator: python main.py"
    echo "3. Check the outputs/ directory for generated reports"
    echo ""
    echo "To deactivate the virtual environment: deactivate"
else
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi
