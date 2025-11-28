#!/bin/bash
# Civic Problem Solver - Quick Setup Script
# ==========================================

echo "🏛️  Civic Problem Solver - Quick Setup"
echo "======================================"

# Check if .env already exists
if [ -f ".env" ]; then
    echo "✅ .env file already exists"
else
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "🔑 IMPORTANT: Edit .env file and add your Anthropic API key!"
    echo "   Required: ANTHROPIC_API_KEY=sk-ant-your-key-here"
    echo "   Get your key from: https://console.anthropic.com"
    echo ""
fi

# Check if Python virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
else
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Created virtual environment"
fi

echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -r api/requirements.txt

echo ""
echo "🎯 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Anthropic API key"
echo "2. Start the backend: cd api && python civic_api_v2.py"
echo "3. Start the frontend: cd frontend && npm install && npm run dev"
echo ""
echo "📖 For detailed instructions, see README.md"