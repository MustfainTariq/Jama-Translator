#!/bin/bash

# Health Check Script for Jama Translation System
# This script verifies that all services are running and accessible

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service endpoints
ADMIN_UI="http://localhost:8081"
DISPLAY_UI="http://localhost:8080"
LIVEKIT_WEB="http://localhost:3000"
WEBSOCKET_WS="ws://localhost:8765"
WEBSOCKET_HTTP="http://localhost:8766"

echo -e "${BLUE}🏥 Jama Translation System - Health Check${NC}"
echo "=================================================="

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local name=$2
    
    if curl -s --max-time 10 "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name is responding${NC}"
        return 0
    else
        echo -e "${RED}✗ $name is not responding${NC}"
        return 1
    fi
}

# Function to check WebSocket endpoint
check_websocket() {
    local url=$1
    local name=$2
    
    # Use netcat to check if port is open
    if nc -z localhost 8765 2>/dev/null; then
        echo -e "${GREEN}✓ $name port is open${NC}"
        return 0
    else
        echo -e "${RED}✗ $name port is not accessible${NC}"
        return 1
    fi
}

# Function to check Docker container
check_container() {
    local container_name=$1
    local service_name=$2
    
    if docker ps --filter "name=$container_name" --filter "status=running" | grep -q "$container_name"; then
        echo -e "${GREEN}✓ $service_name container is running${NC}"
        return 0
    else
        echo -e "${RED}✗ $service_name container is not running${NC}"
        return 1
    fi
}

echo -e "\n${YELLOW}Checking Docker Containers...${NC}"
check_container "jama-admin-ui" "Admin UI"
check_container "jama-admin-backend" "Admin Backend"
check_container "jama-display-ui" "Display UI"
check_container "jama-livekit-web" "LiveKit Web"
check_container "jama-livekit-agent" "LiveKit Agent"
check_container "jama-websocket-server" "WebSocket Server"

echo -e "\n${YELLOW}Checking HTTP Endpoints...${NC}"
check_http "$ADMIN_UI" "Admin Panel UI"
check_http "$DISPLAY_UI" "Display UI"
check_http "$LIVEKIT_WEB" "LiveKit Web Client"
check_http "$WEBSOCKET_HTTP" "WebSocket HTTP Server"

echo -e "\n${YELLOW}Checking WebSocket Connection...${NC}"
check_websocket "$WEBSOCKET_WS" "WebSocket Server"

echo -e "\n${YELLOW}Checking Service Dependencies...${NC}"

# Check if .env file exists
if [ -f .env ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
    
    # Check if required environment variables are set
    if grep -q "LIVEKIT_API_KEY" .env && grep -q "LIVEKIT_API_SECRET" .env; then
        echo -e "${GREEN}✓ LiveKit credentials configured${NC}"
    else
        echo -e "${RED}✗ LiveKit credentials missing in .env${NC}"
    fi
else
    echo -e "${RED}✗ .env file not found${NC}"
fi

# Check Docker network
if docker network ls | grep -q "jama-translation-network"; then
    echo -e "${GREEN}✓ Docker network exists${NC}"
else
    echo -e "${RED}✗ Docker network not found${NC}"
fi

echo "=================================================="

# Summary
echo -e "\n${BLUE}📊 Summary${NC}"
echo "If all checks show ✓, your system is ready to use!"
echo ""
echo "Access your services at:"
echo "• Admin Panel:    $ADMIN_UI"
echo "• Public Display: $DISPLAY_UI"  
echo "• LiveKit Web:    $LIVEKIT_WEB"
echo ""
echo "To view logs: make logs"
echo "To restart:   make restart" 