@echo off
echo Starting Vocal Verse Application...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

REM Check if npm is available
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm is not installed or not in PATH
    echo Please install npm and try again
    pause
    exit /b 1
)

echo All required tools are available.
echo.

REM Install backend dependencies if not already installed
echo Installing backend dependencies...
cd /d "p:\vocal_verse\backend"
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python packages...
pip install -r requirements.txt

echo.

REM Install frontend dependencies if not already installed
echo Installing frontend dependencies...
cd /d "p:\vocal_verse\frontend"
if not exist "node_modules" (
    echo Installing npm packages...
    npm install
)

echo.
echo Starting services...
echo.

REM Start backend in a new window
echo Starting Backend Server (Port 8000)...
start "Vocal Verse Backend" cmd /k "cd /d p:\vocal_verse\backend && venv\Scripts\activate.bat && python server.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
echo Starting Frontend Development Server...
start "Vocal Verse Frontend" cmd /k "cd /d p:\vocal_verse\frontend && npm start"

echo.
echo ================================
echo  Vocal Verse Application Started
echo ================================
echo.
echo Backend Server: http://localhost:8000
echo Frontend App: http://localhost:3000
echo.
echo Press any key to close this window...
echo (The services will continue running in separate windows)
pause >nul