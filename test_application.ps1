#!/usr/bin/env pwsh
# Comprehensive test script for Vocal Verse Application

Write-Host "🧪 Testing Vocal Verse Application..." -ForegroundColor Green
Write-Host ""

# Test backend health
Write-Host "1. Testing Backend Health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET
    $data = $response.Content | ConvertFrom-Json
    if ($data.status -eq "healthy") {
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend health check failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Backend is not accessible: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test frontend accessibility
Write-Host "2. Testing Frontend Accessibility..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend is accessible" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend is not accessible" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Frontend is not accessible: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test voice command - Add product
Write-Host "3. Testing Voice Command - Add Product..." -ForegroundColor Yellow
try {
    $body = @{
        command = "add potato 10 kg at 25 rupees"
        language = "en"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "http://localhost:8000/voice-command" -Method POST -ContentType "application/json" -Body $body
    $data = $response.Content | ConvertFrom-Json
    
    if ($data.success -eq $true) {
        Write-Host "✅ Voice command (add product) works" -ForegroundColor Green
        Write-Host "   Message: $($data.message)" -ForegroundColor Gray
    } else {
        Write-Host "❌ Voice command failed: $($data.message)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Voice command test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test voice command - List products
Write-Host "4. Testing Voice Command - List Products..." -ForegroundColor Yellow
try {
    $body = @{
        command = "list all products"
        language = "en"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "http://localhost:8000/voice-command" -Method POST -ContentType "application/json" -Body $body
    $data = $response.Content | ConvertFrom-Json
    
    if ($data.success -eq $true) {
        Write-Host "✅ Voice command (list products) works" -ForegroundColor Green
        Write-Host "   Found $($data.products.Count) products" -ForegroundColor Gray
    } else {
        Write-Host "❌ Voice command failed: $($data.message)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Voice command test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test voice command - Search product
Write-Host "5. Testing Voice Command - Search Product..." -ForegroundColor Yellow
try {
    $body = @{
        command = "search for tomato"
        language = "en"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "http://localhost:8000/voice-command" -Method POST -ContentType "application/json" -Body $body
    $data = $response.Content | ConvertFrom-Json
    
    if ($data.success -eq $true) {
        Write-Host "✅ Voice command (search product) works" -ForegroundColor Green
        Write-Host "   Product: $($data.product.name) - $($data.product.quantity) kg at ₹$($data.product.price_per_kg)/kg" -ForegroundColor Gray
    } else {
        Write-Host "⚠️ Voice command (search): $($data.message)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Voice command test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test REST API - Get all products
Write-Host "6. Testing REST API - Get Products..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/products" -Method GET
    $data = $response.Content | ConvertFrom-Json
    
    if ($data.success -eq $true) {
        Write-Host "✅ REST API works" -ForegroundColor Green
        Write-Host "   Total products: $($data.products.Count)" -ForegroundColor Gray
        
        # Display products
        foreach ($product in $data.products) {
            Write-Host "   - $($product.name): $($product.quantity) kg at ₹$($product.price_per_kg)/kg" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ REST API failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ REST API test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test CORS (Cross-Origin Resource Sharing)
Write-Host "7. Testing CORS Headers..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/products" -Method GET
    $corsHeader = $response.Headers["Access-Control-Allow-Origin"]
    
    if ($corsHeader -eq "*") {
        Write-Host "✅ CORS is properly configured" -ForegroundColor Green
    } else {
        Write-Host "⚠️ CORS might not be configured correctly" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ CORS test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Application Testing Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "  • Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  • Frontend App: http://localhost:3000" -ForegroundColor White
Write-Host "  • API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🎤 Voice Commands you can try:" -ForegroundColor Cyan
Write-Host "  • Add tomato 5 kg at 20 rupees" -ForegroundColor White
Write-Host "  • List all products" -ForegroundColor White
Write-Host "  • Search for tomato" -ForegroundColor White
Write-Host "  • Add onion 3 kg at 15 rupees" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "  • Use Chrome for best voice recognition support" -ForegroundColor White
Write-Host "  • Make sure microphone permissions are granted" -ForegroundColor White
Write-Host "  • Speak clearly and wait for the response" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
Read-Host