#!/bin/bash
# Quick start script for Civic Problem Solver demo

echo "🏛️  Starting Civic Problem Solver..."
echo

# Check if we're in the right directory
if [ ! -f "api/endpoints/civic_api.py" ]; then
    echo "❌ Please run this script from the civic-problem-solver directory"
    exit 1
fi

# Start backend
echo "🚀 Starting backend on port 8001..."
cd api/endpoints
python civic_api.py &
BACKEND_PID=$!
cd ../..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Function to cleanup processes on exit
cleanup() {
    echo
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

# Trap ctrl+c and cleanup
trap cleanup SIGINT

echo
echo "✅ Services started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend: http://localhost:8001"
echo "📚 Docs: http://localhost:8001/docs"
echo
echo "💡 You'll need to configure your API keys in the frontend"
echo "🔑 Get Anthropic key: https://console.anthropic.com"
echo "🔍 Get Serper key (optional): https://serper.dev"
echo
echo "Press Ctrl+C to stop all services"

# Wait for user to interrupt
wait