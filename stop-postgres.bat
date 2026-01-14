@echo off
chcp 65001 >nul
echo ============================================
echo    Stopping PostgreSQL Server
echo ============================================
echo.

set PGDIR=%~dp0postgresql-18.1-2-windows-x64-binaries\pgsql
set PGDATA=%~dp0postgres_data

"%PGDIR%\bin\pg_ctl.exe" stop -D "%PGDATA%"

if %errorlevel% equ 0 (
    echo.
    echo [OK] PostgreSQL stopped successfully
    echo.
) else (
    echo.
    echo [WARNING] PostgreSQL may not be running
    echo.
)

pause
