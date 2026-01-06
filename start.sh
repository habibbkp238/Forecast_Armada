#!/bin/bash

# Fleet Forecasting Engine - Startup Script
# Developed by Irsandi Habibie

echo "🚛 Fleet Forecasting Engine"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting Fleet Forecasting Engine..."
echo "🌐 The app will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Run the app
streamlit run app.py
