#!/usr/bin/env pwsh
# PowerShell script to start Vocal Verse Application

Write-Host "Starting Vocal Verse Application..." -ForegroundColor Green
Write-Host ""

# Function to check if command exists
function Test-Command {
    param($Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow

if (-not (Test-Command "python")) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Command "node")) {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Command "npm")) {
    Write-Host "ERROR: npm is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install npm and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "All required tools are available." -ForegroundColor Green
Write-Host ""

# Setup backend
Write-Host "Setting up backend..." -ForegroundColor Yellow
Set-Location "p:\vocal_verse\backend"

if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

Write-Host "Installing Python packages..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host ""

# Setup frontend
Write-Host "Setting up frontend..." -ForegroundColor Yellow
Set-Location "p:\vocal_verse\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Cyan
    npm install
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Green
Write-Host ""

# Start backend
Write-Host "Starting Backend Server (Port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'p:\vocal_verse\backend'; .\venv\Scripts\Activate.ps1; python server.py" -WindowStyle Normal

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting Frontend Development Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'p:\vocal_verse\frontend'; npm start" -WindowStyle Normal

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "  Vocal Verse Application Started" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend Server: " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Blue
Write-Host "Frontend App: " -NoNewline
Write-Host "http://localhost:3000" -ForegroundColor Blue
Write-Host ""
Write-Host "Backend API Documentation: " -NoNewline
Write-Host "http://localhost:8000/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Yellow
Write-Host "(The services will continue running in separate windows)" -ForegroundColor Gray
Read-Host