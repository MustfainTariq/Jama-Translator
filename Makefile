# Jama Translation System - Docker Management

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

.PHONY: help build up down logs clean setup dev status restart health

## Show this help message
help:
	@echo "$(BLUE)Jama Translation System - Docker Commands$(RESET)"
	@echo ""
	@echo "$(GREEN)Production Commands:$(RESET)"
	@echo "  make setup    - Initial setup (copy .env template)"
	@echo "  make build    - Build all Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make restart  - Restart all services"
	@echo ""
	@echo "$(GREEN)Development Commands:$(RESET)"
	@echo "  make dev      - Start development environment with hot reload"
	@echo "  make dev-down - Stop development environment"
	@echo ""
	@echo "$(GREEN)Utility Commands:$(RESET)"
	@echo "  make logs     - View logs from all services"
	@echo "  make status   - Show status of all containers"
	@echo "  make health   - Run health check on all services"
	@echo "  make clean    - Remove all containers, images, and volumes"
	@echo "  make rebuild  - Clean build and restart"

## Initial setup - copy environment template
setup:
	@echo "$(YELLOW)Setting up environment...$(RESET)"
	@if [ ! -f .env ]; then \
		cp docker-env-template.txt .env; \
		echo "$(GREEN)✓ Created .env file from template$(RESET)"; \
		echo "$(YELLOW)⚠ Please edit .env with your actual LiveKit credentials$(RESET)"; \
	else \
		echo "$(YELLOW)✓ .env file already exists$(RESET)"; \
	fi

## Build all Docker images
build:
	@echo "$(YELLOW)Building all Docker images...$(RESET)"
	docker-compose build
	@echo "$(GREEN)✓ Build complete$(RESET)"

## Start all services (production)
up: setup
	@echo "$(YELLOW)Starting all services...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)✓ All services started$(RESET)"
	@echo ""
	@echo "$(BLUE)Services are now running:$(RESET)"
	@echo "  • Admin Panel:     http://localhost:8081"
	@echo "  • Display UI:      http://localhost:8080"
	@echo "  • LiveKit Web:     http://localhost:3000"
	@echo "  • WebSocket:       ws://localhost:8765"

## Stop all services
down:
	@echo "$(YELLOW)Stopping all services...$(RESET)"
	docker-compose down
	@echo "$(GREEN)✓ All services stopped$(RESET)"

## Start development environment
dev: setup
	@echo "$(YELLOW)Starting development environment...$(RESET)"
	docker-compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✓ Development environment started$(RESET)"
	@echo ""
	@echo "$(BLUE)Development services are running:$(RESET)"
	@echo "  • Admin Panel:     http://localhost:8081"
	@echo "  • Display UI:      http://localhost:8080"
	@echo "  • LiveKit Web:     http://localhost:3000"
	@echo "  • Admin Backend:   http://localhost:3001"

## Stop development environment
dev-down:
	@echo "$(YELLOW)Stopping development environment...$(RESET)"
	docker-compose -f docker-compose.dev.yml down
	@echo "$(GREEN)✓ Development environment stopped$(RESET)"

## View logs from all services
logs:
	docker-compose logs -f

## Show status of all containers
status:
	@echo "$(BLUE)Container Status:$(RESET)"
	docker-compose ps

## Run health check on all services
health:
	@chmod +x scripts/health-check.sh
	@./scripts/health-check.sh

## Restart all services
restart: down up

## Clean up everything (containers, images, volumes)
clean:
	@echo "$(RED)⚠ This will remove ALL containers, images, and volumes$(RESET)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	@echo "$(YELLOW)Cleaning up...$(RESET)"
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -af --volumes
	@echo "$(GREEN)✓ Cleanup complete$(RESET)"

## Rebuild everything from scratch
rebuild: clean build up 