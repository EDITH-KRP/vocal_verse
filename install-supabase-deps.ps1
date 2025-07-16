# Install Supabase Dependencies Script
# Run this script to install all required dependencies for Supabase integration

Write-Host "🚀 Installing Supabase Dependencies for Vocal Verse" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "❌ Error: Please run this script from the vocal_verse root directory" -ForegroundColor Red
    exit 1
}

# Install Backend Dependencies
Write-Host "`n📦 Installing Backend Dependencies..." -ForegroundColor Yellow
Set-Location backend

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Install Python packages
Write-Host "Installing Python packages from requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

# Install Frontend Dependencies
Write-Host "`n📦 Installing Frontend Dependencies..." -ForegroundColor Yellow
Set-Location ../frontend

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 16+ first." -ForegroundColor Red
    exit 1
}

# Install npm packages
Write-Host "Installing npm packages..." -ForegroundColor Cyan
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}

# Return to root directory
Set-Location ..

Write-Host "`n🎉 All dependencies installed successfully!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Set up your Supabase project (see SUPABASE_SETUP_GUIDE.md)" -ForegroundColor White
Write-Host "2. Create .env files with your Supabase credentials" -ForegroundColor White
Write-Host "3. Run the database schema in Supabase SQL Editor" -ForegroundColor White
Write-Host "4. Start the backend: cd backend && python supabase_server.py" -ForegroundColor White
Write-Host "5. Start the frontend: cd frontend && npm start" -ForegroundColor White

Write-Host "`n📖 For detailed setup instructions, see:" -ForegroundColor Cyan
Write-Host "   SUPABASE_SETUP_GUIDE.md" -ForegroundColor White

Write-Host "`n🔧 New Features Available:" -ForegroundColor Magenta
Write-Host "   ✅ User Authentication & Registration" -ForegroundColor Green
Write-Host "   ✅ Cloud Database Storage (PostgreSQL)" -ForegroundColor Green
Write-Host "   ✅ Advanced Analytics Dashboard" -ForegroundColor Green
Write-Host "   ✅ Stock Prediction & Forecasting" -ForegroundColor Green
Write-Host "   ✅ Low Stock Alerts & Recommendations" -ForegroundColor Green
Write-Host "   ✅ Transaction History & Reporting" -ForegroundColor Green
Write-Host "   ✅ Real-time Data Synchronization" -ForegroundColor Green