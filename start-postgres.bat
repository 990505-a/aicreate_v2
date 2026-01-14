@echo off
chcp 65001 >nul
echo ============================================
echo    Starting PostgreSQL Server
echo ============================================
echo.

set PGDIR=%~dp0postgresql-18.1-2-windows-x64-binaries\pgsql
set PGDATA=%~dp0postgres_data
set PGLOG=%PGDATA%\postgresql.log

:: Check if data directory exists
if not exist "%PGDATA%" (
    echo [ERROR] PostgreSQL data directory not found
    echo.
    echo Please initialize PostgreSQL first:
    echo   init-postgres.bat
    echo.
    pause
    exit /b 1
)

:: Start PostgreSQL
echo [INFO] Starting PostgreSQL server...
echo Data directory: %PGDATA%
echo Log file: %PGLOG%
echo.
echo Press Ctrl+C to stop the server
echo.

"%PGDIR%\bin\pg_ctl.exe" start -D "%PGDATA%" -l "%PGLOG%"

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo [OK] PostgreSQL started successfully!
    echo ============================================
    echo.
    echo Server is running in background.
    echo You can close this window safely.
    echo.
    echo Check status: test-postgres.bat
    echo Stop server: stop-postgres.bat
    echo.
) else (
    echo.
    echo [ERROR] Failed to start PostgreSQL
    echo.
    echo Check log file: %PGLOG%
    echo.
    type "%PGLOG%" | findstr /i "error fatal"
    echo.
)

pause
