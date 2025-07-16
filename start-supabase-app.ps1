# Start Supabase-Enhanced Vocal Verse Application
# This script starts both backend and frontend servers with Supabase integration

Write-Host "🚀 Starting Vocal Verse with Supabase Integration" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "❌ Error: Please run this script from the vocal_verse root directory" -ForegroundColor Red
    exit 1
}

# Check for environment files
Write-Host "`n🔍 Checking configuration..." -ForegroundColor Yellow

$backendEnvExists = Test-Path "backend/.env"
$frontendEnvExists = Test-Path "frontend/.env"

if (-not $backendEnvExists) {
    Write-Host "⚠️  Warning: backend/.env file not found" -ForegroundColor Yellow
    Write-Host "   Please create it with your Supabase credentials" -ForegroundColor White
    Write-Host "   See SUPABASE_SETUP_GUIDE.md for details" -ForegroundColor White
}

if (-not $frontendEnvExists) {
    Write-Host "⚠️  Warning: frontend/.env file not found" -ForegroundColor Yellow
    Write-Host "   Please create it with your Supabase credentials" -ForegroundColor White
    Write-Host "   See SUPABASE_SETUP_GUIDE.md for details" -ForegroundColor White
}

if (-not $backendEnvExists -or -not $frontendEnvExists) {
    Write-Host "`n❌ Missing environment configuration. Please set up .env files first." -ForegroundColor Red
    Write-Host "   Run: Get-Content .env.example" -ForegroundColor White
    Write-Host "   Then create .env files in backend/ and frontend/ directories" -ForegroundColor White
    exit 1
}

Write-Host "✅ Configuration files found" -ForegroundColor Green

# Function to start backend
function Start-Backend {
    Write-Host "`n🔧 Starting Backend Server (Supabase-Enhanced)..." -ForegroundColor Yellow
    Set-Location backend
    
    # Check if supabase_server.py exists
    if (-not (Test-Path "supabase_server.py")) {
        Write-Host "❌ supabase_server.py not found in backend directory" -ForegroundColor Red
        return $false
    }
    
    # Start the enhanced backend server
    Start-Process -FilePath "python" -ArgumentList "supabase_server.py" -WindowStyle Normal
    
    Write-Host "✅ Backend server starting on http://localhost:8000" -ForegroundColor Green
    Write-Host "   📊 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "   🔐 Authentication endpoints available" -ForegroundColor Cyan
    Write-Host "   📈 Analytics endpoints available" -ForegroundColor Cyan
    
    Set-Location ..
    return $true
}

# Function to start frontend
function Start-Frontend {
    Write-Host "`n🎨 Starting Frontend Server (Enhanced UI)..." -ForegroundColor Yellow
    Set-Location frontend
    
    # Check if package.json exists
    if (-not (Test-Path "package.json")) {
        Write-Host "❌ package.json not found in frontend directory" -ForegroundColor Red
        return $false
    }
    
    # Start the enhanced frontend
    Start-Process -FilePath "npm" -ArgumentList "start" -WindowStyle Normal
    
    Write-Host "✅ Frontend server starting on http://localhost:3000" -ForegroundColor Green
    Write-Host "   🎤 Voice commands with authentication" -ForegroundColor Cyan
    Write-Host "   📊 Analytics dashboard available" -ForegroundColor Cyan
    Write-Host "   🔐 User registration and login" -ForegroundColor Cyan
    
    Set-Location ..
    return $true
}

# Start both servers
$backendStarted = Start-Backend
$frontendStarted = Start-Frontend

if ($backendStarted -and $frontendStarted) {
    Write-Host "`n🎉 Vocal Verse Application Started Successfully!" -ForegroundColor Green
    Write-Host "=================================================" -ForegroundColor Green
    
    Write-Host "`n🌐 Application URLs:" -ForegroundColor Yellow
    Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
    
    Write-Host "`n🆕 New Features Available:" -ForegroundColor Magenta
    Write-Host "   ✅ User Authentication (Register/Login)" -ForegroundColor Green
    Write-Host "   ✅ Secure Cloud Database Storage" -ForegroundColor Green
    Write-Host "   ✅ Advanced Analytics Dashboard" -ForegroundColor Green
    Write-Host "   ✅ Stock Prediction & Forecasting" -ForegroundColor Green
    Write-Host "   ✅ Low Stock Alerts & Recommendations" -ForegroundColor Green
    Write-Host "   ✅ Transaction History Tracking" -ForegroundColor Green
    Write-Host "   ✅ Real-time Data Synchronization" -ForegroundColor Green
    
    Write-Host "`n🎤 Enhanced Voice Commands:" -ForegroundColor Cyan
    Write-Host "   • 'Add tomato 5 kg at 20 rupees'" -ForegroundColor White
    Write-Host "   • 'Predict tomato stock for 7 days'" -ForegroundColor White
    Write-Host "   • 'Analyze tomato consumption'" -ForegroundColor White
    Write-Host "   • 'Show low stock alerts'" -ForegroundColor White
    Write-Host "   • 'List all products'" -ForegroundColor White
    
    Write-Host "`n📱 How to Use:" -ForegroundColor Yellow
    Write-Host "   1. Open http://localhost:3000 in your browser" -ForegroundColor White
    Write-Host "   2. Register a new account or login" -ForegroundColor White
    Write-Host "   3. Use voice commands to manage inventory" -ForegroundColor White
    Write-Host "   4. Check the Analytics tab for insights" -ForegroundColor White
    Write-Host "   5. Get predictions and stock recommendations" -ForegroundColor White
    
    Write-Host "`n⚠️  Important Notes:" -ForegroundColor Yellow
    Write-Host "   • Make sure your Supabase project is set up correctly" -ForegroundColor White
    Write-Host "   • Database schema should be created in Supabase" -ForegroundColor White
    Write-Host "   • Environment variables must be configured" -ForegroundColor White
    Write-Host "   • Use Chrome/Edge for best voice recognition support" -ForegroundColor White
    
    Write-Host "`n🔧 Troubleshooting:" -ForegroundColor Red
    Write-Host "   • If authentication fails, check Supabase credentials" -ForegroundColor White
    Write-Host "   • If database errors occur, verify schema creation" -ForegroundColor White
    Write-Host "   • Check browser console for frontend errors" -ForegroundColor White
    Write-Host "   • See SUPABASE_SETUP_GUIDE.md for detailed help" -ForegroundColor White
    
    Write-Host "`n📊 Monitor your servers in the opened terminal windows" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C in each terminal to stop the servers" -ForegroundColor White
    
} else {
    Write-Host "`n❌ Failed to start one or more servers" -ForegroundColor Red
    Write-Host "Please check the error messages above and try again" -ForegroundColor White
}