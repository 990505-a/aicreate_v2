@echo off
chcp 65001 >nul
echo ============================================
echo    Starting Redis Server
echo ============================================
echo.

cd /d %~dp0redis_win32

echo Starting Redis server...
echo Redis will run in foreground mode.
echo Press Ctrl+C to stop the server.
echo.

redis-server.exe redis.windows.conf

pause
