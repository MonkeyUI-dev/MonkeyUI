#!/bin/bash

# MonkeyUI Authentication Setup Script
# This script helps you set up the authentication system

set -e

echo "=================================================="
echo "MonkeyUI Authentication System Setup"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the project root
if [ ! -f "package.json" ] && [ ! -d "backend" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo "Step 1: Backend Setup"
echo "---------------------"

cd backend

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
if command -v uv &> /dev/null; then
    uv sync
else
    echo -e "${RED}Error: uv is not installed. Please install uv first.${NC}"
    echo "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
uv run python manage.py makemigrations
uv run python manage.py migrate

# Create superuser prompt
echo ""
read -p "Do you want to create a superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Creating superuser...${NC}"
    uv run python manage.py createsuperuser
fi

cd ..

echo ""
echo "Step 2: Frontend Setup"
echo "---------------------"

cd frontend

# Install Node dependencies
echo -e "${YELLOW}Installing Node dependencies...${NC}"
npm install

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}Creating .env.local file...${NC}"
    cp .env.example .env.local || cat > .env.local << EOF
# API Configuration
VITE_API_URL=http://localhost:8000/api
EOF
    echo -e "${GREEN}.env.local created${NC}"
else
    echo -e "${GREEN}.env.local already exists${NC}"
fi

cd ..

echo ""
echo "=================================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "To start the development servers:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  uv run python manage.py runserver"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Access the application at:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000/api"
echo "  Django Admin: http://localhost:8000/admin"
echo "  API Docs: http://localhost:8000/api/docs/"
echo ""
echo "Documentation:"
echo "  See docs/AUTHENTICATION.md for detailed usage"
echo ""
