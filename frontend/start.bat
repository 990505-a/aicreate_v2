@echo off
chcp 65001 >nul
echo ============================================
echo    AICreate Frontend - Local Startup
echo ============================================
echo.

:: Check Node.js installation
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 18 or higher from: https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js found
node --version

:: Check npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not installed
    pause
    exit /b 1
)

echo [OK] npm found
npm --version
echo.

:: Check if node_modules exists
if not exist node_modules (
    echo [INFO] node_modules not found
    echo [INFO] Installing dependencies...
    echo This may take a few minutes on first run...
    echo.
    npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
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
        echo [OK] .env file created
        echo.
        echo [INFO] You may need to edit .env to configure API URL
    ) else (
        echo [INFO] No .env file found (may not be required)
        echo [INFO] Using default Vite configuration
    )
) else (
    echo [OK] .env file exists
)

:: Start the dev server
echo.
echo ============================================
echo    Starting Frontend Dev Server
echo ============================================
echo.
echo URL:      http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

npm run dev

:: On exit
echo.
echo Frontend server stopped
