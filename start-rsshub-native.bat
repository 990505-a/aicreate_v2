@echo off
chcp 65001 >nul
echo ============================================
echo    Starting RSSHub (Local Deployment)
echo ============================================
echo.

set RSSHUB_DIR=%~dp0rsshub

:: Check if Node.js is installed
echo [1/4] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js installed

:: Check if RSSHub directory exists
echo.
echo [2/4] Checking RSSHub directory...
if not exist "%RSSHUB_DIR%" (
    echo [ERROR] RSSHub directory not found: %RSSHUB_DIR%
    pause
    exit /b 1
)
echo [OK] RSSHub directory exists

:: Check if RSSHub is built
echo.
echo [3/4] Checking RSSHub build...
if not exist "%RSSHUB_DIR%\dist\index.mjs" (
    echo [ERROR] RSSHub not built
    echo [INFO] Please build RSSHub first:
    echo   cd rsshub
    echo   npm install
    echo   npm run build
    pause
    exit /b 1
)
echo [OK] RSSHub is built

:: Check if PM2 is installed
echo.
echo [4/4] Checking PM2...
pm2 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] PM2 not found, installing...
    npm install -g pm2
    if %errorlevel% neq 0 (
        echo [ERROR] PM2 installation failed
        pause
        exit /b 1
    )
    echo [OK] PM2 installed
) else (
    echo [OK] PM2 installed
)

:: Start RSSHub
echo.
echo ============================================
echo Starting RSSHub Service
echo ============================================
echo.
echo Configuration:
echo   - Port: 1200
echo   - Cache: Redis (localhost:6381)
echo   - Mode: Production
echo.

cd /d "%RSSHUB_DIR%"

:: Stop existing instance if running
pm2 describe rsshub >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Stopping existing RSSHub instance...
    pm2 stop rsshub
    pm2 delete rsshub
    timeout /t 2 /nobreak >nul
)

:: Start RSSHub with PM2
echo [INFO] Starting RSSHub with PM2...
pm2 start dist/index.mjs --name rsshub --env production

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start RSSHub
    pause
    exit /b 1
)

:: Save PM2 configuration
pm2 save

:: Wait for RSSHub to start
echo [INFO] Waiting for RSSHub to initialize...
timeout /t 5 /nobreak >nul

:: Check RSSHub status
echo.
echo [INFO] Checking RSSHub status...
pm2 status

echo.
echo ============================================
echo [OK] RSSHub Started Successfully!
echo ============================================
echo.
echo Service Info:
echo   - Status: Running
echo   - Access: http://localhost:1200
echo   - Health: http://localhost:1200/healthz
echo   - API: http://localhost:1200/api
echo.
echo Management Commands:
echo   - Status:   pm2 status
echo   - Logs:     pm2 logs rsshub
echo   - Stop:     pm2 stop rsshub
echo   - Restart:  pm2 restart rsshub
echo   - Delete:   pm2 delete rsshub
echo.
pause
