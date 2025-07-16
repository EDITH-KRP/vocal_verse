#!/usr/bin/env pwsh
# PowerShell script to stop Vocal Verse Application

Write-Host "Stopping Vocal Verse Application..." -ForegroundColor Yellow
Write-Host ""

# Function to kill processes by port
function Stop-ProcessByPort {
    param($Port)
    
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connections) {
            foreach ($conn in $connections) {
                $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "Stopping process: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Cyan
                    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                }
            }
        }
    }
    catch {
        # Port might not be in use
    }
}

# Stop backend server
Write-Host "Stopping Backend Server (Port 8000)..." -ForegroundColor Cyan
Stop-ProcessByPort -Port 8000

# Stop frontend development server
Write-Host "Stopping Frontend Development Server (Port 3000)..." -ForegroundColor Cyan
Stop-ProcessByPort -Port 3000

# Clean up any remaining processes
Write-Host "Cleaning up any remaining processes..." -ForegroundColor Cyan

# Stop Node.js processes
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    foreach ($proc in $nodeProcesses) {
        Write-Host "Stopping Node.js process (PID: $($proc.Id))" -ForegroundColor Gray
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

# Stop Python processes (be careful not to kill system Python processes)
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    foreach ($proc in $pythonProcesses) {
        # Only kill if it's likely our server process
        if ($proc.Path -like "*vocal_verse*" -or $proc.CommandLine -like "*server.py*") {
            Write-Host "Stopping Python process (PID: $($proc.Id))" -ForegroundColor Gray
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host ""
Write-Host "Vocal Verse Application has been stopped." -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit"