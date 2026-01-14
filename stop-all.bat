@echo off
chcp 65001 >nul
cls
echo.
echo ============================================
echo    Stopping All AICreate Services
echo ============================================
echo.

set PGDIR=%~dp0postgresql-18.1-2-windows-x64-binaries\pgsql
set PGDATA=%~dp0postgres_data

echo [1/4] Stopping Backend...
tasklist | findstr python.exe >nul 2>&1
if %errorlevel% equ 0 (
    taskkill /F /IM python.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Backend stopped
    ) else (
        echo [INFO] Backend may not be running
    )
) else (
    echo [INFO] Backend is not running
)
timeout /t 1 /nobreak >nul

echo.
echo [2/5] Stopping Frontend...
tasklist | findstr node.exe >nul 2>&1
if %errorlevel% equ 0 (
    taskkill /F /IM node.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Frontend stopped
    ) else (
        echo [INFO] Frontend may not be running
    )
) else (
    echo [INFO] Frontend is not running
)
timeout /t 1 /nobreak >nul

echo.
echo [3/5] Stopping RSSHub...
pm2 --version >nul 2>&1
if %errorlevel% equ 0 (
    pm2 describe rsshub >nul 2>&1
    if %errorlevel% equ 0 (
        pm2 stop rsshub >nul 2>&1
        pm2 delete rsshub >nul 2>&1
        echo [OK] RSSHub stopped
    ) else (
        echo [INFO] RSSHub is not running
    )
) else (
    echo [INFO] PM2 not installed (RSSHub not managed)
)
timeout /t 1 /nobreak >nul

echo.
echo [4/5] Stopping Redis...
tasklist | findstr redis-server >nul 2>&1
if %errorlevel% equ 0 (
    taskkill /F /IM redis-server.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Redis stopped
    ) else (
        echo [INFO] Redis may not be running
    )
) else (
    echo [INFO] Redis is not running
)
timeout /t 1 /nobreak >nul

echo.
echo [5/5] Stopping PostgreSQL...
if exist "%PGDATA%" (
    "%PGDIR%\bin\pg_ctl.exe" stop -D "%PGDATA%" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] PostgreSQL stopped
    ) else (
        echo [INFO] PostgreSQL may not be running
    )
) else (
    echo [INFO] PostgreSQL data directory not found
)

echo.
echo.
echo ============================================
echo    All Services Stopped
echo ============================================
echo.
pause
