# Complete Vercel Deployment Script
# AI Voice Inventory Management System

param(
    [string]$GeminiApiKey = "",
    [string]$MongoUrl = "",
    [switch]$SkipTests = $false
)

Write-Host "🚀 AI Voice Inventory Management System - Vercel Deployment" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Yellow

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check prerequisites
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Cyan

# Check Node.js
if (Test-Command "node") {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js is not installed. Please install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check Git
if (Test-Command "git") {
    $gitVersion = git --version
    Write-Host "✅ Git version: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Git is not installed. Please install from https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# Check Python
if (Test-Command "python") {
    $pythonVersion = python --version
    Write-Host "✅ Python version: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python is not installed. Please install from https://python.org/" -ForegroundColor Red
    exit 1
}

# Install/check Vercel CLI
Write-Host "`n🌐 Setting up Vercel CLI..." -ForegroundColor Cyan
if (-not (Test-Command "vercel")) {
    Write-Host "📦 Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Vercel CLI" -ForegroundColor Red
        exit 1
    }
}

$vercelVersion = vercel --version
Write-Host "✅ Vercel CLI version: $vercelVersion" -ForegroundColor Green

# Check environment variables
Write-Host "`n🔐 Checking environment variables..." -ForegroundColor Cyan

if (-not $GeminiApiKey) {
    if (Test-Path ".env") {
        Write-Host "📄 Found .env file, loading variables..." -ForegroundColor Yellow
        Get-Content ".env" | ForEach-Object {
            if ($_ -match "GEMINI_API_KEY=(.+)") {
                $GeminiApiKey = $matches[1]
            }
            if ($_ -match "MONGO_URL=(.+)") {
                $MongoUrl = $matches[1]
            }
        }
    }
}

if (-not $GeminiApiKey) {
    Write-Host "⚠️  GEMINI_API_KEY not set" -ForegroundColor Yellow
    $GeminiApiKey = Read-Host "Please enter your Gemini API Key"
}

if (-not $MongoUrl) {
    Write-Host "⚠️  MONGO_URL not set" -ForegroundColor Yellow
    $MongoUrl = Read-Host "Please enter your MongoDB connection string"
}

if ($GeminiApiKey -and $MongoUrl) {
    Write-Host "✅ Environment variables configured" -ForegroundColor Green
} else {
    Write-Host "❌ Missing required environment variables" -ForegroundColor Red
    Write-Host "Please set GEMINI_API_KEY and MONGO_URL" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`n📚 Installing dependencies..." -ForegroundColor Cyan

# Frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Set-Location ..
Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green

# Backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Backend dependencies installed" -ForegroundColor Green

# Run deployment check
if (-not $SkipTests) {
    Write-Host "`n🧪 Running deployment readiness check..." -ForegroundColor Cyan
    
    # Create temporary .env for testing
    $tempEnv = @"
GEMINI_API_KEY=$GeminiApiKey
MONGO_URL=$MongoUrl
"@
    $tempEnv | Out-File -FilePath ".env" -Encoding UTF8
    
    python deploy-check.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Some deployment checks failed, but continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "✅ All deployment checks passed" -ForegroundColor Green
    }
}

# Initialize Git if needed
Write-Host "`n📁 Checking Git repository..." -ForegroundColor Cyan
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    git add .
    git commit -m "Initial commit: AI Voice Inventory Management System"
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository found" -ForegroundColor Green
}

# Check for GitHub remote
$hasRemote = git remote get-url origin 2>$null
if (-not $hasRemote) {
    Write-Host "`n🔗 GitHub Setup Required" -ForegroundColor Yellow
    Write-Host "To deploy to Vercel, you need to push your code to GitHub first." -ForegroundColor Yellow
    Write-Host "`nSteps to create GitHub repository:" -ForegroundColor Cyan
    Write-Host "1. Go to https://github.com/new" -ForegroundColor White
    Write-Host "2. Create a new repository named 'ai-voice-inventory'" -ForegroundColor White
    Write-Host "3. Copy the repository URL" -ForegroundColor White
    Write-Host "4. Run this command with your URL:" -ForegroundColor White
    Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/ai-voice-inventory.git" -ForegroundColor Green
    Write-Host "   git branch -M main" -ForegroundColor Green
    Write-Host "   git push -u origin main" -ForegroundColor Green
    
    $continueWithoutGithub = Read-Host "`nDo you want to continue with local deployment only? (y/N)"
    if ($continueWithoutGithub -ne "y" -and $continueWithoutGithub -ne "Y") {
        Write-Host "Please set up GitHub repository and run this script again." -ForegroundColor Yellow
        exit 0
    }
}

# Deploy to Vercel
Write-Host "`n🚀 Deploying to Vercel..." -ForegroundColor Cyan

# Login to Vercel if needed
Write-Host "Checking Vercel authentication..." -ForegroundColor Yellow
vercel whoami 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Vercel..." -ForegroundColor Yellow
    vercel login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to login to Vercel" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Vercel authentication confirmed" -ForegroundColor Green

# Deploy
Write-Host "`nStarting deployment..." -ForegroundColor Yellow
Write-Host "⚠️  When prompted:" -ForegroundColor Yellow
Write-Host "   - Project name: ai-voice-inventory (or your choice)" -ForegroundColor Cyan
Write-Host "   - Link to existing project: N" -ForegroundColor Cyan
Write-Host "   - Directory: ./ (default)" -ForegroundColor Cyan

vercel --prod
$deploymentStatus = $LASTEXITCODE

if ($deploymentStatus -eq 0) {
    Write-Host "`n🎉 Deployment successful!" -ForegroundColor Green
    
    # Get deployment URL
    $vercelUrl = vercel --prod --json | ConvertFrom-Json | Select-Object -ExpandProperty url
    if ($vercelUrl) {
        Write-Host "`n🌐 Your app is live at: https://$vercelUrl" -ForegroundColor Green
        
        # Update frontend .env.production
        Write-Host "`nUpdating frontend production environment..." -ForegroundColor Yellow
        "REACT_APP_BACKEND_URL=https://$vercelUrl" | Out-File -FilePath "frontend/.env.production" -Encoding UTF8
        Write-Host "✅ Frontend environment updated" -ForegroundColor Green
    }
    
    Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Add environment variables in Vercel dashboard:" -ForegroundColor White
    Write-Host "   - GEMINI_API_KEY=$GeminiApiKey" -ForegroundColor Gray
    Write-Host "   - MONGO_URL=$MongoUrl" -ForegroundColor Gray
    Write-Host "2. Go to https://vercel.com/dashboard" -ForegroundColor White
    Write-Host "3. Select your project → Settings → Environment Variables" -ForegroundColor White
    Write-Host "4. Add the variables above" -ForegroundColor White
    Write-Host "5. Redeploy the project" -ForegroundColor White
    
    Write-Host "`n🧪 Test your deployment:" -ForegroundColor Cyan
    if ($vercelUrl) {
        Write-Host "   - Backend API: https://$vercelUrl/api/health" -ForegroundColor White
        Write-Host "   - Frontend: https://$vercelUrl" -ForegroundColor White
    }
    Write-Host "   - Try voice commands" -ForegroundColor White
    Write-Host "   - Check AI suggestions" -ForegroundColor White
    Write-Host "   - Test analytics dashboard" -ForegroundColor White
    
} else {
    Write-Host "`n❌ Deployment failed" -ForegroundColor Red
    Write-Host "Please check the errors above and try again." -ForegroundColor Red
    Write-Host "`nCommon solutions:" -ForegroundColor Yellow
    Write-Host "- Ensure you're logged into Vercel: vercel login" -ForegroundColor White
    Write-Host "- Check your internet connection" -ForegroundColor White
    Write-Host "- Verify all files are committed to Git" -ForegroundColor White
    exit 1
}

Write-Host "`n" + "=" * 70 -ForegroundColor Yellow
Write-Host "🎯 Deployment Complete!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Yellow

# Save deployment info
$deploymentInfo = @"
# AI Voice Inventory Management System - Deployment Info
Deployed: $(Get-Date)
Vercel URL: https://$vercelUrl
Environment Variables Required:
- GEMINI_API_KEY (configured)
- MONGO_URL (configured)

Next steps:
1. Add environment variables in Vercel dashboard
2. Test all features
3. Monitor performance
"@

$deploymentInfo | Out-File -FilePath "deployment-info.txt" -Encoding UTF8
Write-Host "📄 Deployment info saved to deployment-info.txt" -ForegroundColor Green