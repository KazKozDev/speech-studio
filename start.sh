#!/bin/bash

# Speech Studio - Auto Start Script for macOS
# Simply double-click this file to start the application

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Starting Speech Studio..."
echo "📁 Project directory: $PROJECT_DIR"

# Clean up port 8000 if it's in use
PORT=8000
echo "🧹 Checking for processes on port $PORT..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PID=$(lsof -Pi :$PORT -sTCP:LISTEN -t)
    echo "⚠️  Found process on port $PORT (PID: $PID). Killing it..."
    kill -9 $PID 2>/dev/null || true
    sleep 1
    echo "✅ Port $PORT is now free"
else
    echo "✅ Port $PORT is available"
fi

# Navigate to backend
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install --quiet -r requirements.txt
fi

# Get the port
PORT=8000
echo "✅ Server will run on http://localhost:$PORT"

# Start server in background
echo "🔧 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port $PORT &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Open browser
echo "🌐 Opening browser..."
open "http://localhost:$PORT"

echo ""
echo "================================================"
echo "✅ Speech Studio is running!"
echo "🔗 http://localhost:$PORT"
echo "📝 Press Ctrl+C in terminal to stop the server"
echo "================================================"
echo ""

# Keep script running
wait $SERVER_PID
