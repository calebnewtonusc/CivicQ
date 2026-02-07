.PHONY: help setup dev clean test lint format docker-up docker-down migrate health

help:
	@echo "CivicQ Development Commands"
	@echo "==========================="
	@echo ""
	@echo "make setup       - Set up development environment"
	@echo "make dev         - Start development servers"
	@echo "make docker-up   - Start all services with Docker Compose"
	@echo "make docker-down - Stop all Docker services"
	@echo "make test        - Run all tests"
	@echo "make lint        - Run linters"
	@echo "make format      - Format code"
	@echo "make migrate     - Run database migrations"
	@echo "make health      - Check system health"
	@echo "make clean       - Clean build artifacts"

setup:
	@chmod +x scripts/setup-dev.sh
	@./scripts/setup-dev.sh

dev:
	@echo "Starting development servers..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:3000"
	@docker-compose up

docker-up:
	@docker-compose up -d
	@echo "Services started! Check status with: docker-compose ps"

docker-down:
	@docker-compose down

test:
	@echo "Running backend tests..."
	@cd backend && source venv/bin/activate && pytest
	@echo "Running frontend tests..."
	@cd frontend && npm test -- --watchAll=false

lint:
	@echo "Linting backend..."
	@cd backend && source venv/bin/activate && flake8 app/
	@echo "Linting frontend..."
	@cd frontend && npm run lint

format:
	@echo "Formatting backend..."
	@cd backend && source venv/bin/activate && black app/
	@echo "Formatting frontend..."
	@cd frontend && npm run format

migrate:
	@cd backend && source venv/bin/activate && alembic upgrade head

health:
	@chmod +x scripts/health-check.sh
	@./scripts/health-check.sh

clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf backend/venv
	@rm -rf frontend/build
	@echo "Clean complete!"
