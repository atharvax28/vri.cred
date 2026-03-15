#!/bin/bash
# Development startup script for both frontend and backend

# Install backend dependencies with uv if pyproject.toml exists
if [ -f "demo/backend/pyproject.toml" ]; then
    echo "Installing backend dependencies..."
    cd demo/backend
    uv sync --no-dev || pip install -r requirements.txt
    cd ../..
fi

# Start frontend static server in background
echo "Starting frontend server on port 3000..."
cd demo/frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ../..

# Start backend FastAPI server
echo "Starting backend server on port 8000..."
cd demo/backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ../..

# Handle cleanup
cleanup() {
    echo "Shutting down servers..."
    kill $FRONTEND_PID $BACKEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Frontend running on http://localhost:3000"
echo "Backend running on http://localhost:8000"
echo "Press Ctrl+C to stop..."

wait
