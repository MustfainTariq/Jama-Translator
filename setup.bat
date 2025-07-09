@echo off
echo 🚀 Jama Translation System - Docker Setup

REM Check if .env exists, if not create it
if not exist .env (
    echo 📝 Creating .env file from template...
    copy docker-env-template.txt .env
    echo ✅ Created .env file from template
    echo ⚠️  Please edit .env with your actual LiveKit credentials
) else (
    echo ✅ .env file already exists
)

echo.
echo 🔨 Building Docker images...
docker-compose build

if %errorlevel% equ 0 (
    echo ✅ Build completed successfully
    echo.
    echo 🚀 Starting all services...
    docker-compose up -d
    
    if %errorlevel% equ 0 (
        echo ✅ All services started successfully
        echo.
        echo 🌐 Your services are now running at:
        echo   • Admin Panel:     http://localhost:8081
        echo   • Display UI:      http://localhost:8080
        echo   • LiveKit Web:     http://localhost:3000
        echo   • WebSocket:       ws://localhost:8765
        echo.
        echo 📊 To check status: docker-compose ps
        echo 📋 To view logs:    docker-compose logs -f
        echo 🛑 To stop:         docker-compose down
    ) else (
        echo ❌ Failed to start services
        echo 📋 Check logs with: docker-compose logs
    )
) else (
    echo ❌ Build failed
    echo 📋 Check the error messages above
)

pause 