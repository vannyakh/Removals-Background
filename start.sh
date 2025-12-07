#!/bin/bash

echo "================================================"
echo "🎨 Background Removal Tool - Setup & Start"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Create models directory
mkdir -p service/models

# Check if model exists
if [ ! -f "service/models/u2net.pth" ]; then
    echo ""
    echo "⚠️  Model weights not found!"
    echo "📥 Downloading U²-Net model (~176 MB)..."
    echo ""
    python service/download_model.py
    echo ""
fi

# Start the server
echo ""
echo "================================================"
echo "🚀 Starting Backend Server..."
echo "================================================"
echo ""
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To use the application:"
echo "   1. Open client/index.html in your browser"
echo "   OR"
echo "   2. Run: cd client && python -m http.server 3000"
echo "      Then visit: http://localhost:3000"
echo ""
echo "Press CTRL+C to stop"
echo "================================================"
echo ""

python main.py

