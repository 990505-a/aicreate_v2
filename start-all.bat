@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cls
echo.
echo ============================================
echo    AICreate Platform - One-Click Startup
echo ============================================
echo.
echo This script will automatically:
echo   1. Initialize Redis and PostgreSQL (if needed)
echo   2. Start all services (Redis, PostgreSQL, RSSHub, Backend, Frontend)
echo   3. Open browser when ready
echo.
echo ============================================
echo.

:: ============================================================================
:: Step 1: Check and Initialize PostgreSQL
:: ============================================================================
echo [1/6] Checking PostgreSQL...
set PGDIR=%~dp0postgresql-18.1-2-windows-x64-binaries\pgsql
set PGDATA=%~dp0postgres_data
set PGBIN=%PGDIR%\bin

if not exist "%PGDATA%" (
    echo [INFO] PostgreSQL data directory not found
    echo [INFO] Initializing PostgreSQL...
    echo.
    echo ===========================================================
    echo   PostgreSQL Initialization
    echo ===========================================================
    echo.
    echo Password will be set to: postgres
    echo Please enter password when prompted
    echo.
    pause

    mkdir "%PGDATA%"

    echo.
    echo [INFO] Running initdb...
    "%PGBIN%\initdb.exe" -D "%PGDATA%" -U postgres -E UTF8

    if %errorlevel% neq 0 (
        echo [ERROR] Failed to initialize PostgreSQL
        pause
        exit /b 1
    )

    echo.
    echo [OK] PostgreSQL initialized successfully!
) else (
    echo [OK] PostgreSQL data directory exists
)

:: ============================================================================
:: Step 2: Start PostgreSQL
:: ============================================================================
echo.
echo [2/6] Starting PostgreSQL...

"%PGBIN%\pg_ctl.exe" status -D "%PGDATA%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Starting PostgreSQL server...
    start "PostgreSQL Server" /min cmd /c "%PGBIN%\pg_ctl.exe start -D %PGDATA% -l %PGDATA%\postgresql.log && pause"
    echo [INFO] Waiting for PostgreSQL to be ready...
)

:: Wait for PostgreSQL to be ready (max 30 seconds)
set /a COUNT=0
:WAIT_PG
timeout /t 2 /nobreak >nul
set /a COUNT+=2

"%PGBIN%\pg_isready" -U postgres >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] PostgreSQL is responding, waiting for full initialization...
    :: Additional wait for PostgreSQL to fully initialize
    timeout /t 5 /nobreak >nul

    :: Test actual connection
    "%PGBIN%\psql.exe" -U postgres -c "SELECT 1;" >nul 2>&1
    if !errorlevel! equ 0 (
        if !COUNT! gtr 0 (
            echo [OK] PostgreSQL is fully ready - waited !COUNT! seconds
        ) else (
            echo [OK] PostgreSQL is already running and ready
        )
        goto PG_READY
    )
)

if !COUNT! lss 90 (
    if !COUNT! equ 2 (
        echo [INFO] Waiting for PostgreSQL to be ready...
    )
    echo [INFO] Still waiting... ^(!COUNT!s/90s^)
    goto WAIT_PG
)

echo [ERROR] PostgreSQL failed to start within 90 seconds
echo [INFO] Check log: %PGDATA%\postgresql.log
pause
exit /b 1

:PG_READY

:: ============================================================================
:: Step 3: Create Database if not exists
:: ============================================================================
echo.
echo [3/6] Checking/Creating database...

"%PGBIN%\psql.exe" -U postgres -c "\l" | findstr aicreate >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Creating database: aicreate...
    "%PGBIN%\createdb.exe" -U postgres aicreate
    if %errorlevel% equ 0 (
        echo [OK] Database created
    ) else (
        echo [WARNING] Database may already exist
    )
) else (
    echo [OK] Database exists
)

:: Test database connection
echo [INFO] Testing database connection...
"%PGBIN%\psql.exe" -U postgres -d aicreate -c "SELECT 1;" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Database connection verified
) else (
    echo [ERROR] Cannot connect to database
    pause
    exit /b 1
)

:: ============================================================================
:: Step 4: Stop old Redis and Start new Redis (port 6381)
:: ============================================================================
echo.
echo [4/6] Starting Redis on port 6381...

:: Stop any existing Redis
tasklist | findstr redis-server >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Stopping old Redis instances...
    taskkill /F /IM redis-server.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

:: Start Redis on new port
echo [INFO] Starting Redis server (port 6381)...
start "Redis Server" /min cmd /c "cd /d %~dp0redis_win32 && redis-server.exe redis.windows.conf"
timeout /t 3 /nobreak >nul

:: Verify Redis is running
tasklist | findstr redis-server >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Redis started successfully on port 6381
) else (
    echo [ERROR] Redis failed to start
    pause
    exit /b 1
)

:: ============================================================================
:: Step 5: Start RSSHub
:: ============================================================================
echo.
echo [5/6] Starting RSSHub...

:: Check if PM2 is installed
pm2 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] PM2 not found, installing...
    npm install -g pm2
    if %errorlevel% neq 0 (
        echo [WARNING] PM2 installation failed, RSSHub will not be started
        goto SKIP_RSSHUB
    )
)

:: Check if RSSHub is built
set RSSHUB_DIR=%~dp0rsshub
if not exist "%RSSHUB_DIR%\dist\index.mjs" (
    echo [WARNING] RSSHub not built, skipping...
    echo [INFO] To build RSSHub:
    echo   cd rsshub
    echo   npm install
    echo   npm run build
    goto SKIP_RSSHUB
)

:: Stop existing RSSHub instance
pm2 describe rsshub >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Stopping existing RSSHub instance...
    pm2 stop rsshub
    pm2 delete rsshub
    timeout /t 2 /nobreak >nul
)

:: Start RSSHub
echo [INFO] Starting RSSHub with PM2...
cd /d "%RSSHUB_DIR%"
pm2 start dist/index.mjs --name rsshub
if %errorlevel% equ 0 (
    pm2 save
    echo [OK] RSSHub started on port 1200
    timeout /t 3 /nobreak >nul
) else (
    echo [WARNING] Failed to start RSSHub
)

:SKIP_RSSHUB

:: ============================================================================
:: Step 6: Start Backend and Frontend
:: ============================================================================
echo.
echo [6/6] Starting Backend and Frontend...

:: Check if virtual environment exists
if not exist "%~dp0.venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found
    echo [INFO] Please run: python -m venv .venv
    pause
    exit /b 1
)

:: Check if backend is already running
tasklist | findstr python.exe | findstr "uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Starting Backend...
    echo [INFO] Waiting for services to stabilize...
    timeout /t 3 /nobreak >nul

    start "AICreate Backend" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 7002 --reload"

    echo [INFO] Waiting for backend to initialize - this may take 10-15 seconds...
    timeout /t 10 /nobreak >nul

    :: Verify backend is responding
    echo [INFO] Checking backend health...
    curl -s http://localhost:7002/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Backend is healthy and ready
    ) else (
        echo [WARNING] Backend health check failed
        echo [INFO] Check backend window for errors
    )
) else (
    echo [OK] Backend is already running
)

:: Check if frontend is already running
tasklist | findstr node.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Starting Frontend...
    cd /d %~dp0frontend
    start "AICreate Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
    echo [OK] Frontend starting...
) else (
    echo [OK] Frontend is already running
)

:: ============================================================================
:: Final Summary
:: ============================================================================
echo.
echo.
echo ============================================
echo    All Services Started!
echo ============================================
echo.
echo Startup Sequence:
echo   ✓ PostgreSQL  (localhost:5432)
echo   ✓ Redis       (localhost:6381)
echo   ✓ RSSHub      (localhost:1200)
echo   ✓ Backend     (http://localhost:7002)
echo   ✓ Frontend    (http://localhost:5173)
echo.
echo ============================================
echo.
echo Services:
echo   - PostgreSQL Server
echo   - Redis Server (port 6381)
echo   - RSSHub Server (port 1200)
echo   - AICreate Backend (port 7002)
echo   - AICreate Frontend (port 5173)
echo.
echo Access URLs:
echo   - Frontend:       http://localhost:5173
echo   - API Docs:       http://localhost:7002/docs
echo   - ReDoc:          http://localhost:7002/redoc
echo   - Health Check:   http://localhost:7002/health
echo   - RSSHub:         http://localhost:1200
echo.
echo Opening browser...
echo.

:: Wait a bit for services to fully start
timeout /t 3 /nobreak >nul

:: Open browser
start http://localhost:5173

echo.
echo ============================================
echo.
echo To stop all services:
echo   Close all opened windows
echo   Or run: stop-all.bat
echo.
echo ============================================
echo.
echo Press any key to close this window...
pause >nul
