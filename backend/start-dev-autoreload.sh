#!/bin/bash
# Development startup script for designmonkey backend
# This script starts Django and Celery with auto-reload on code changes

set -e

echo "🚀 Starting designmonkey Backend Services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Start Celery worker in background with auto-reload
echo -e "${YELLOW}🔧 Starting Celery worker with auto-reload...${NC}"
uv run watchmedo auto-restart \
    --directory=./apps \
    --pattern="*.py" \
    --recursive \
    -- celery -A config worker --loglevel=info &
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
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ${GREEN}Services Running${NC}              ${BLUE}║${NC}"
echo -e "${BLUE}╠════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC} Django:  http://localhost:8000          ${BLUE}║${NC}"
echo -e "${BLUE}║${NC} Celery:  Worker with auto-reload       ${BLUE}║${NC}"
echo -e "${BLUE}║${NC} Logs:    Output to console             ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "  • Code changes in ${GREEN}apps/${NC} will auto-restart Celery"
echo -e "  • Press ${RED}Ctrl+C${NC} to stop all services"
echo -e "  • Celery logs appear directly in this terminal"
echo ""

uv run python manage.py runserver

# Wait for background processes
wait
