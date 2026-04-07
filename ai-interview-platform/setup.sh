#!/bin/bash
# AI Interview Platform - Complete Setup Script
# Run this script to set up the entire project

set -e  # Exit on error

echo "======================================"
echo "AI Interview Platform - Setup Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${YELLOW}Checking Prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3.10+ not found. Please install Python.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js not found. Please install Node.js 18+.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${RED}PostgreSQL not found. Please install PostgreSQL.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ PostgreSQL found${NC}"

# Setup Backend
echo -e "\n${YELLOW}Setting up Backend...${NC}"

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found!${NC}"
    echo "Please create .env file with required variables:"
    echo "  - DATABASE_URL"
    echo "  - GROQ_API_KEY"
    echo "  - SECRET_KEY"
    echo "See .env.example for template"
fi

cd ..

# Setup Frontend
echo -e "\n${YELLOW}Setting up Frontend...${NC}"

cd frontend

echo "Installing Node dependencies..."
npm install

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

cd ..

# Summary
echo -e "\n${GREEN}======================================"
echo "Setup Complete! 🎉"
echo "======================================${NC}"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Configure backend/.env with:"
echo "   - Database URL: postgresql://user:password@localhost:5432/ai_interview_db"
echo "   - GROQ_API_KEY: Get from https://console.groq.com"
echo "   - SECRET_KEY: Generate a secure random string (min 32 chars)"
echo ""
echo "2. Create PostgreSQL database:"
echo "   psql -U postgres -d ai_interview_db < DATABASE_SCHEMA.sql"
echo ""
echo "3. Start Backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python -m uvicorn app.main:app --reload"
echo ""
echo "4. Start Frontend (in new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "5. Access:"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Frontend: http://localhost:3000"
echo ""
echo -e "${GREEN}Happy Interviewing! 🚀${NC}"
