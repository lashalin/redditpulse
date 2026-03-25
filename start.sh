#!/bin/bash

echo "========================================="
echo "  Reddit Marketing Tool - Setup & Start"
echo "========================================="

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo ""
    echo "[1/4] Creating .env from template..."
    cp backend/.env.example backend/.env
    echo "  => IMPORTANT: Edit backend/.env and add your API keys:"
    echo "     - REDDIT_CLIENT_ID (get from https://www.reddit.com/prefs/apps)"
    echo "     - REDDIT_CLIENT_SECRET"
    echo "     - GEMINI_API_KEY (get from https://aistudio.google.com/apikey)"
    echo ""
    echo "  After editing .env, run this script again."
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

echo ""
echo "[2/4] Building containers..."
docker compose build

echo ""
echo "[3/4] Starting services..."
docker compose up -d

echo ""
echo "[4/4] Waiting for services to be ready..."
sleep 5

# Run migrations
echo "  Running database migrations..."
docker compose exec backend alembic revision --autogenerate -m "initial" 2>/dev/null
docker compose exec backend alembic upgrade head

echo ""
echo "========================================="
echo "  All services are running!"
echo "========================================="
echo ""
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "  To stop:   docker compose down"
echo "  To logs:   docker compose logs -f"
echo "========================================="
