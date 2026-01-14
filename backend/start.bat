@echo off
chcp 65001 >nul
echo ============================================
echo    AICreate Backend - Local Startup
echo ============================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

:: Check if root virtual environment exists
if not exist ..\.venv (
    echo [INFO] Root virtual environment not found
    echo Creating virtual environment at D:\aicreate_v2\.venv...
    cd ..
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        echo Please ensure Python 3.13 is installed
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created at D:\aicreate_v2\.venv
    cd backend
)

:: Activate virtual environment
echo [INFO] Activating virtual environment from D:\aicreate_v2\.venv...
call ..\.venv\Scripts\activate.bat

:: Check if requirements are installed
echo.
echo [INFO] Checking dependencies...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

:: Check .env file
echo.
if not exist .env (
    if exist .env.example (
        echo [WARNING] .env file not found
        echo [INFO] Creating .env from .env.example...
        copy .env.example .env
        echo.
        echo [IMPORTANT] Please edit .env and configure:
        echo   - Database connection (DATABASE_URL)
        echo   - Redis connection (REDIS_URL)
        echo   - API keys (OPENAI_API_KEY, etc.)
        echo.
        pause
    ) else (
        echo [ERROR] Neither .env nor .env.example found
        pause
        exit /b 1
    )
) else (
    echo [OK] .env file exists
)

:: Start the server
echo.
echo ============================================
echo    Starting Backend Server
echo ============================================
echo.
echo API:      http://localhost:7002
echo Docs:     http://localhost:7002/docs
echo Redoc:    http://localhost:7002/redoc
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 7002 --reload

:: Deactivate virtual environment on exit
deactivate
