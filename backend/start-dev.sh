#!/bin/bash
# Development startup script for MonkeyUI backend
# This script starts all required services for local development

set -e

echo "🚀 Starting MonkeyUI Backend Services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Redis is running
echo -e "${YELLOW}📊 Checking Redis...${NC}"
if ! nc -z localhost 6379 2>/dev/null; then
    echo -e "${RED}❌ Redis is not running on localhost:6379${NC}"
    echo -e "${YELLOW}💡 Start Redis with: brew services start redis${NC}"
    echo -e "${YELLOW}   Or use Docker: docker run -d -p 6379:6379 redis:7-alpine${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Redis is running${NC}"

# Check if PostgreSQL is running
echo -e "${YELLOW}📊 Checking PostgreSQL...${NC}"
if ! nc -z localhost 5432 2>/dev/null; then
    echo -e "${RED}❌ PostgreSQL is not running on localhost:5432${NC}"
    echo -e "${YELLOW}💡 Start with Docker: docker-compose up -d db${NC}"
    exit 1
fi
echo -e "${GREEN}✓ PostgreSQL is running${NC}"

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Celery worker in background
echo -e "${YELLOW}🔧 Starting Celery worker...${NC}"
uv run celery -A config worker --loglevel=info &
CELERY_PID=$!
sleep 2

if ps -p $CELERY_PID > /dev/null; then
    echo -e "${GREEN}✓ Celery worker started (PID: $CELERY_PID)${NC}"
else
    echo -e "${RED}❌ Failed to start Celery worker${NC}"
    exit 1
fi

# Start Django development server
echo -e "${YELLOW}🌐 Starting Django server...${NC}"
echo -e "${GREEN}✓ All services running!${NC}"
echo -e "\n${YELLOW}Services:${NC}"
echo -e "  Django:  http://localhost:8000"
echo -e "  Celery:  Worker running (logs in console)"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}\n"

uv run python manage.py runserver

# Wait for background processes
wait
