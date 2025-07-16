@echo off
echo Stopping Vocal Verse Application...
echo.

REM Kill processes by port (more reliable than process name)
echo Stopping Backend Server (Port 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /pid %%a /f >nul 2>&1
)

echo Stopping Frontend Development Server (Port 3000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    taskkill /pid %%a /f >nul 2>&1
)

REM Also kill common Node.js and Python processes that might be running
echo Cleaning up any remaining processes...
taskkill /im node.exe /f >nul 2>&1
taskkill /im python.exe /f >nul 2>&1

echo.
echo Vocal Verse Application has been stopped.
echo.
pause