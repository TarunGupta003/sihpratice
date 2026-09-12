#!/bin/bash
# ORCA Ultimate - Web Execution Script
# Runs backend + frontend web

echo "=== ORCA Ultimate Web Execution ==="
echo "Step 1: Backend (ORCA Box Brain) at http://localhost:8000"
echo "Step 2: Frontend Web at http://localhost:5173"

# Kill any old
pkill -f "uvicorn main:app" 2>/dev/null || true

cd backend
echo "Installing backend deps..."
pip install -r requirements.txt -q

echo "Starting backend..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

sleep 3
curl -s http://localhost:8000/ | head -c 200
echo

cd frontend-web
echo "Installing frontend deps..."
npm install --silent

echo "Starting frontend..."
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== READY ==="
echo "Backend: http://localhost:8000/docs"
echo "Frontend: http://localhost:5173"
echo "Health: http://localhost:8000/api/v1/health"
echo "Advisory: http://localhost:8000/api/v1/advisory?lat=20.9&lon=70.37"
echo ""
echo "Press Ctrl+C to stop both"
wait $BACKEND_PID $FRONTEND_PID
