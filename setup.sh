#!/bin/bash

# designmonkey Setup Script
# This script sets up the development environment for designmonkey

set -e

echo "🐒 designmonkey Setup Script"
echo "========================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm found: $(npm --version)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python is not installed. Please install Python 3.14+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"

# Check uv
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠ uv is not installed. Installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env 2>/dev/null || true
fi
echo -e "${GREEN}✓ uv found${NC}"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠ PostgreSQL is not installed${NC}"
    echo "Please install PostgreSQL 15+ with pgvector extension"
    echo "macOS: brew install postgresql pgvector"
else
    echo -e "${GREEN}✓ PostgreSQL found${NC}"
fi

echo ""
echo "Setting up frontend..."
echo "======================"

cd frontend

if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ frontend/package.json not found${NC}"
    exit 1
fi

echo "Installing frontend dependencies..."
npm install

echo -e "${GREEN}✓ Frontend setup complete${NC}"

cd ..

echo ""
echo "Setting up backend..."
echo "====================="

cd backend

if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ backend/pyproject.toml not found${NC}"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please update backend/.env with your database credentials${NC}"
fi

echo "Installing backend dependencies..."
uv sync

echo -e "${GREEN}✓ Backend setup complete${NC}"

cd ..

echo ""
echo "📝 Next Steps:"
echo "=============="
echo ""
echo "1. Setup PostgreSQL database:"
echo "   createdb designmonkey_dev"
echo "   psql designmonkey_dev -c 'CREATE EXTENSION vector;'"
echo ""
echo "2. Update backend/.env with your database credentials"
echo ""
echo "3. Run migrations:"
echo "   cd backend"
echo "   uv run python manage.py migrate"
echo "   uv run python manage.py createsuperuser"
echo ""
echo "4. Start the development servers:"
echo ""
echo "   Terminal 1 - Frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "   Terminal 2 - Backend:"
echo "   cd backend && uv run python manage.py runserver"
echo ""
echo -e "${GREEN}✨ Setup complete!${NC}"
