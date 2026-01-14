@echo off
chcp 65001 >nul
echo ============================================
echo    Stopping RSSHub (Local Deployment)
echo ============================================
echo.

:: Check if PM2 is installed
pm2 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] PM2 not installed
    echo [INFO] Nothing to stop
    pause
    exit /b 0
)

:: Check if RSSHub is running
pm2 describe rsshub >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] RSSHub is not running
    pause
    exit /b 0
)

:: Stop RSSHub
echo [INFO] Stopping RSSHub...
pm2 stop rsshub
if %errorlevel% equ 0 (
    echo [OK] RSSHub stopped
) else (
    echo [ERROR] Failed to stop RSSHub
)

:: Delete RSSHub from PM2
echo [INFO] Removing RSSHub from PM2...
pm2 delete rsshub
if %errorlevel% equ 0 (
    echo [OK] RSSHub removed from PM2
) else (
    echo [WARNING] Failed to remove RSSHub from PM2
)

:: Save PM2 configuration
pm2 save

echo.
echo ============================================
echo [OK] RSSHub Stopped!
echo ============================================
echo.
pause
