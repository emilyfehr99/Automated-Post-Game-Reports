#!/bin/bash

# All Three Zones API Setup Script

echo "🚀 Setting up All Three Zones API..."
echo "======================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env_example.txt .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file with your All Three Zones credentials"
else
    echo "✅ .env file already exists"
fi

# Make scripts executable
chmod +x run.py
chmod +x test_setup.py
chmod +x example_client.py

echo "✅ Scripts made executable"

# Run setup tests
echo "🧪 Running setup tests..."
python3 test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your All Three Zones credentials"
    echo "2. Start the API server: python3 run.py"
    echo "3. Test the API: python3 example_client.py"
    echo ""
    echo "API will be available at: http://localhost:8000"
    echo "API documentation: http://localhost:8000/docs"
else
    echo "❌ Setup tests failed. Please check the errors above."
    exit 1
fi 