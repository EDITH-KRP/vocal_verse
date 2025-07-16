# PowerShell script for setting up Vercel deployment
# AI Voice Inventory Management System

Write-Host "🚀 Setting up AI Voice Inventory Management System for Vercel Deployment" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Yellow

# Check if Node.js is installed
Write-Host "`n📦 Checking Node.js installation..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
Write-Host "`n🐍 Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version
    Write-Host "✅ Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python from https://python.org/" -ForegroundColor Red
    exit 1
}

# Install frontend dependencies
Write-Host "`n📚 Installing frontend dependencies..." -ForegroundColor Cyan
Set-Location frontend
try {
    npm install
    Write-Host "✅ Frontend dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Set-Location ..

# Install backend dependencies
Write-Host "`n🔧 Installing backend dependencies..." -ForegroundColor Cyan
try {
    pip install -r backend/requirements.txt
    Write-Host "✅ Backend dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

# Install Vercel CLI
Write-Host "`n🌐 Installing Vercel CLI..." -ForegroundColor Cyan
try {
    npm install -g vercel
    Write-Host "✅ Vercel CLI installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install Vercel CLI" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
Write-Host "`n🔐 Checking environment configuration..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found. Creating template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please edit .env file with your API keys before deploying" -ForegroundColor Yellow
}

# Run deployment check
Write-Host "`n🧪 Running deployment readiness check..." -ForegroundColor Cyan
try {
    python deploy-check.py
} catch {
    Write-Host "❌ Deployment check failed. Please fix issues before deploying." -ForegroundColor Red
}

# Display next steps
Write-Host "`n" + "=" * 70 -ForegroundColor Yellow
Write-Host "🎯 SETUP COMPLETE! Next Steps:" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Yellow

Write-Host "`n1. Configure Environment Variables:" -ForegroundColor Cyan
Write-Host "   • Edit .env file with your API keys"
Write-Host "   • Get Gemini API key: https://makersuite.google.com/app/apikey"
Write-Host "   • Set up MongoDB Atlas: https://mongodb.com/atlas"

Write-Host "`n2. Test Locally:" -ForegroundColor Cyan
Write-Host "   • Backend: python backend/server.py"
Write-Host "   • Frontend: cd frontend && npm start"
Write-Host "   • Demo: python backend/test_ai_system.py"

Write-Host "`n3. Deploy to Vercel:" -ForegroundColor Cyan
Write-Host "   • Push code to Git repository"
Write-Host "   • Run: vercel"
Write-Host "   • Follow prompts to deploy"

Write-Host "`n4. Configure Production:" -ForegroundColor Cyan
Write-Host "   • Add environment variables in Vercel dashboard"
Write-Host "   • Update frontend/.env.production with your domain"
Write-Host "   • Test all features"

Write-Host "`n🔗 Useful Links:" -ForegroundColor Cyan
Write-Host "   • Vercel Dashboard: https://vercel.com/dashboard"
Write-Host "   • Deployment Guide: ./DEPLOYMENT_GUIDE.md"
Write-Host "   • AI Features Guide: ./backend/AI_FEATURES_README.md"

Write-Host "`n🎉 Ready to deploy your AI-powered inventory system!" -ForegroundColor Green