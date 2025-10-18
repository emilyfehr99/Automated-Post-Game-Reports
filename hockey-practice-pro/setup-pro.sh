#!/bin/bash

echo "🏒 Setting up Hockey Practice Pro..."
echo "=================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
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

# Create environment file
echo "🔧 Creating environment configuration..."
cat > .env.local << EOF
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here

# Firebase Configuration (for user data storage)
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyCm2m3lSlh_IBgHSOLcmeCO9lZYHaxgrFw
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=hockey-practice-planner.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=hockey-practice-planner
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=hockey-practice-planner.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=557366268618
NEXT_PUBLIC_FIREBASE_APP_ID=1:557366268618:web:d6f5cf9e80045d966fda33

# Stripe Configuration (for payments)
STRIPE_SECRET_KEY=your-stripe-secret-key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
EOF

echo "✅ Environment file created (.env.local)"
echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Update .env.local with your actual API keys"
echo "2. Run 'npm run dev' to start the development server"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "📝 Don't forget to:"
echo "- Set up Stripe for payment processing"
echo "- Configure your Firebase project for user data"
echo "- Update the branding and contact information"
echo ""
echo "🚀 Ready to launch your hockey practice planning business!"
