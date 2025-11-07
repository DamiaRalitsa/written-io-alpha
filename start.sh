#!/bin/bash

# Written - AI Activity Generator
# Startup script to ensure proper virtual environment activation

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "🚀 Starting Written AI Chatbot..."
echo "📁 Project directory: $SCRIPT_DIR"

# Activate virtual environment
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "🔧 Activating virtual environment..."
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -d "$SCRIPT_DIR/.venv" ]; then
    echo "🔧 Activating virtual environment..."
    source "$SCRIPT_DIR/.venv/bin/activate"
else
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "⚠️  Environment file (.env) not found!"
    echo "📝 Please copy .env.example to .env and configure your settings:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Start the application
echo "🌐 Starting Flask application..."
echo "📱 Open your browser and go to: http://127.0.0.1:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

cd "$SCRIPT_DIR"
python3 app.py
