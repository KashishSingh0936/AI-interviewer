@echo off
REM AI Interview Platform - Windows Setup Script
REM Run this script to set up the entire project

setlocal enabledelayedexpansion

echo ======================================
echo AI Interview Platform - Setup Script
echo ======================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10+ not found. Please install Python.
    exit /b 1
)
echo OK: Python found

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js 18+.
    exit /b 1
)
echo OK: Node.js found

REM Setup Backend
echo.
echo Setting up Backend...
cd backend

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo OK: Backend dependencies installed

REM Check .env file
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env file with required variables
    echo See .env.example for template
)

cd ..

REM Setup Frontend
echo.
echo Setting up Frontend...
cd frontend

echo Installing Node dependencies...
call npm install

echo OK: Frontend dependencies installed

cd ..

REM Summary
echo.
echo ======================================
echo Setup Complete 
echo ======================================

echo.
echo Next Steps:
echo 1. Configure backend\.env with:
echo    - Database URL
echo    - GROQ_API_KEY
echo    - SECRET_KEY
echo.
echo 2. Create PostgreSQL database:
echo    psql -U postgres -d ai_interview_db -f DATABASE_SCHEMA.sql
echo.
echo 3. Start Backend:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python -m uvicorn app.main:app --reload
echo.
echo 4. Start Frontend (in new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 5. Access:
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo    Frontend: http://localhost:3000
echo.
echo Happy Interviewing!
