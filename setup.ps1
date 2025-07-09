#!/usr/bin/env pwsh

# Jama Translation System - Windows Setup Script

Write-Host "🚀 Jama Translation System - Docker Setup" -ForegroundColor Blue
Write-Host ""

# Check if .env exists, if not create it
if (!(Test-Path .env)) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item docker-env-template.txt .env
    Write-Host "✅ Created .env file from template" -ForegroundColor Green
    Write-Host "⚠️  Please edit .env with your actual LiveKit credentials" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔨 Building Docker images..." -ForegroundColor Yellow
docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build completed successfully" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Starting all services..." -ForegroundColor Yellow
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All services started successfully" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Your services are now running at:" -ForegroundColor Blue
        Write-Host "  • Admin Panel:     http://localhost:8081" -ForegroundColor Cyan
        Write-Host "  • Display UI:      http://localhost:8080" -ForegroundColor Cyan
        Write-Host "  • LiveKit Web:     http://localhost:3000" -ForegroundColor Cyan
        Write-Host "  • WebSocket:       ws://localhost:8765" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📊 To check status: docker-compose ps" -ForegroundColor Gray
        Write-Host "📋 To view logs:    docker-compose logs -f" -ForegroundColor Gray
        Write-Host "🛑 To stop:         docker-compose down" -ForegroundColor Gray
    } else {
        Write-Host "❌ Failed to start services" -ForegroundColor Red
        Write-Host "📋 Check logs with: docker-compose logs" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Build failed" -ForegroundColor Red
    Write-Host "📋 Check the error messages above" -ForegroundColor Yellow
} 