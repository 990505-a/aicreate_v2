@echo off
chcp 65001 >nul
echo ============================================
echo    Initializing PostgreSQL Database
echo ============================================
echo.

set PGDIR=%~dp0postgresql-18.1-2-windows-x64-binaries\pgsql
set PGDATA=%~dp0postgres_data
set PGLOG=%PGDATA%\postgresql.log

:: Create data directory if not exists
if not exist "%PGDATA%" (
    echo [INFO] Creating PostgreSQL data directory: %PGDATA%
    mkdir "%PGDATA%"
) else (
    echo [WARNING] Data directory already exists
    set /p continue=Do you want to reinitialize? This will DELETE all data! Press y or n:
    if /i not "%continue%"=="y" (
        echo [INFO] Initialization cancelled
        pause
        exit /b 0
    )
    echo [INFO] Removing existing data directory...
    rmdir /s /q "%PGDATA%"
    mkdir "%PGDATA%"
)

:: Initialize database
echo.
echo [INFO] Initializing PostgreSQL database cluster...
echo.
echo Setting superuser password to: postgres
echo.
"%PGDIR%\bin\initdb.exe" -D "%PGDATA%" -U postgres -W -E UTF8

if %errorlevel% neq 0 (
    echo [ERROR] Failed to initialize PostgreSQL
    pause
    exit /b 1
)

echo.
echo ============================================
echo [OK] PostgreSQL initialized successfully!
echo ============================================
echo.
echo Data directory: %PGDATA%
echo Next steps:
echo   1. Start PostgreSQL: start-postgres.bat
echo   2. Create database: create-database.bat
echo.
pause
