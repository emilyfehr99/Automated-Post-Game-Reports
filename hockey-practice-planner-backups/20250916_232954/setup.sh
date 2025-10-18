#!/bin/bash

echo "🏒 Setting up Hockey Practice Planner..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p public/images
mkdir -p public/drills
mkdir -p public/practice-plans

echo "✅ Project directories created"

# Copy any existing drill images if they exist
if [ -f "../ihs-print-1757448115819.pdf" ]; then
    echo "📄 Found drill PDF, you can process it later for drill images"
fi

echo ""
echo "🎉 Setup complete! To start the development server:"
echo "   npm run dev"
echo ""
echo "🌐 Then open http://localhost:3000 in your browser"
echo ""
echo "📚 Check README.md for more information about features and usage"
