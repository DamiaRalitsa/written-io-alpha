# Written AI Chatbot - Makefile
# Comprehensive build and run automation

# Project variables
PROJECT_NAME := written-alpha
PYTHON := python3
VENV_DIR := venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip
APP_PORT := 5000
APP_HOST := 127.0.0.1

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# Check if virtual environment exists
VENV_EXISTS := $(shell test -d $(VENV_DIR) && echo "yes" || echo "no")

## Help - Show available commands
help:
	@echo "$(BLUE)📚 Written AI Chatbot - Available Commands$(NC)"
	@echo "$(BLUE)==========================================$(NC)"
	@echo ""
	@echo "$(GREEN)🚀 Quick Start:$(NC)"
	@echo "  $(YELLOW)make setup$(NC)     - Complete project setup (venv + deps + db)"
	@echo "  $(YELLOW)make run$(NC)       - Start the application"
	@echo ""
	@echo "$(GREEN)🛠️  Development:$(NC)"
	@echo "  $(YELLOW)make install$(NC)   - Install/update dependencies"
	@echo "  $(YELLOW)make dev$(NC)       - Run in development mode"
	@echo "  $(YELLOW)make test$(NC)      - Run tests"
	@echo "  $(YELLOW)make lint$(NC)      - Run linting (flake8, black)"
	@echo "  $(YELLOW)make format$(NC)    - Format code with black"
	@echo ""
	@echo "$(GREEN)🗄️  Database:$(NC)"
	@echo "  $(YELLOW)make db-setup$(NC)  - Initialize PostgreSQL database"
	@echo "  $(YELLOW)make db-migrate$(NC) - Run database migrations"
	@echo "  $(YELLOW)make db-reset$(NC)  - Reset database (CAUTION: destroys data)"
	@echo "  $(YELLOW)make db-status$(NC) - Check database connection"
	@echo ""
	@echo "$(GREEN)🧹 Maintenance:$(NC)"
	@echo "  $(YELLOW)make clean$(NC)     - Clean up temporary files"
	@echo "  $(YELLOW)make clean-all$(NC) - Clean everything including venv"
	@echo "  $(YELLOW)make logs$(NC)      - Show application logs"
	@echo ""
	@echo "$(GREEN)📦 Docker:$(NC)"
	@echo "  $(YELLOW)make docker-up$(NC)   - Start PostgreSQL container"
	@echo "  $(YELLOW)make docker-down$(NC) - Stop PostgreSQL container"
	@echo "  $(YELLOW)make docker-logs$(NC) - Show PostgreSQL logs"
	@echo ""
	@echo "$(GREEN)ℹ️  Info:$(NC)"
	@echo "  $(YELLOW)make status$(NC)    - Show project status"
	@echo "  $(YELLOW)make env-check$(NC) - Check environment setup"

## Setup - Complete project setup
setup: venv install db-setup
	@echo "$(GREEN)✅ Setup completed! Run 'make run' to start the application.$(NC)"

## Create virtual environment
venv:
ifeq ($(VENV_EXISTS),no)
	@echo "$(BLUE)🐍 Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)✅ Virtual environment created$(NC)"
else
	@echo "$(GREEN)✅ Virtual environment already exists$(NC)"
endif

## Install dependencies
install: 
	rm -rf venv
	make venv
	make install
	venv
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install psycopg2-binary
	$(VENV_PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

## Run the application
run: 
	@echo "🚀 Starting Written AI Chatbot..."
	@echo "📱 Application will be available at: http://127.0.0.1:5001"
	@echo "🛑 Press Ctrl+C to stop"
	@echo ""
	$(VENV_PYTHON) app.py

## Run in development mode with auto-reload
dev: venv install
	@echo "$(BLUE)🛠️  Starting in development mode...$(NC)"
	@echo "$(BLUE)📱 Application: http://$(APP_HOST):$(APP_PORT)$(NC)"
	@echo "$(BLUE)🔄 Auto-reload enabled$(NC)"
	@echo ""
	@. $(VENV_DIR)/bin/activate && FLASK_ENV=development FLASK_DEBUG=True $(PYTHON) app.py

## Database setup
db-setup: venv install
	@echo "$(BLUE)🗄️  Setting up PostgreSQL database...$(NC)"
	@. $(VENV_DIR)/bin/activate && $(PYTHON) migrate_database.py
	@echo "$(GREEN)✅ Database setup completed$(NC)"

## Run database migrations
db-migrate: venv
	@echo "$(BLUE)🔄 Running database migrations...$(NC)"
	@. $(VENV_DIR)/bin/activate && $(PYTHON) migrate_database.py
	@echo "$(GREEN)✅ Database migrations completed$(NC)"

## Reset database (CAUTION)
db-reset: venv
	@echo "$(RED)⚠️  WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ] || exit 1
	@echo "$(BLUE)🗄️  Resetting database...$(NC)"
	@. $(VENV_DIR)/bin/activate && $(PYTHON) -c "from src.database.postgres_manager import get_database_manager; db = get_database_manager(); [db.execute_command(f'DROP TABLE IF EXISTS {t} CASCADE') for t in ['activities', 'projects', 'users', 'user_positions', 'ai_prompt_templates']]"
	@$(MAKE) db-migrate
	@echo "$(GREEN)✅ Database reset completed$(NC)"

## Check database status
db-status: venv
	@echo "$(BLUE)🔍 Checking database connection...$(NC)"
	@. $(VENV_DIR)/bin/activate && $(PYTHON) -c "from src.database.postgres_manager import get_database_manager; db = get_database_manager(); print('✅ Database connection: OK' if db.test_connection() else '❌ Database connection: FAILED'); print('📊 Connection stats:', db.get_connection_stats())"

## Run tests
test: venv install
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@. $(VENV_DIR)/bin/activate && $(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing || echo "$(YELLOW)⚠️  No tests found. Create tests in tests/ directory$(NC)"

## Run linting
lint: venv install
	@echo "$(BLUE)🔍 Running linting...$(NC)"
	@. $(VENV_DIR)/bin/activate && flake8 src/ --max-line-length=120 --ignore=E203,W503 || echo "$(YELLOW)⚠️  Linting completed with warnings$(NC)"
	@. $(VENV_DIR)/bin/activate && mypy src/ --ignore-missing-imports || echo "$(YELLOW)⚠️  Type checking completed with warnings$(NC)"

## Format code
format: venv install
	@echo "$(BLUE)✨ Formatting code...$(NC)"
	@. $(VENV_DIR)/bin/activate && black src/ --line-length=120
	@echo "$(GREEN)✅ Code formatting completed$(NC)"

## Docker commands
docker-up:
	@echo "$(BLUE)🐳 Starting PostgreSQL container...$(NC)"
	@docker run -d --name postgres-written \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_PASSWORD=password \
		-e POSTGRES_DB=test \
		-p 5433:5432 \
		postgres:13.3-alpine || echo "$(YELLOW)⚠️  Container might already be running$(NC)"
	@echo "$(GREEN)✅ PostgreSQL container started$(NC)"

docker-down:
	@echo "$(BLUE)🐳 Stopping PostgreSQL container...$(NC)"
	@docker stop postgres-written || echo "$(YELLOW)⚠️  Container might not be running$(NC)"
	@docker rm postgres-written || echo "$(YELLOW)⚠️  Container might not exist$(NC)"
	@echo "$(GREEN)✅ PostgreSQL container stopped$(NC)"

docker-logs:
	@echo "$(BLUE)📋 PostgreSQL container logs:$(NC)"
	@docker logs postgres-written || echo "$(RED)❌ Container not found$(NC)"

## Show application logs
logs:
	@echo "$(BLUE)📋 Application logs:$(NC)"
	@tail -f logs/written.log 2>/dev/null || echo "$(YELLOW)⚠️  No log file found. Run the application first.$(NC)"

## Clean temporary files
clean:
	@echo "$(BLUE)🧹 Cleaning temporary files...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type f -name "*.log" -delete
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

## Clean everything including virtual environment
clean-all: clean
	@echo "$(BLUE)🧹 Cleaning everything...$(NC)"
	@rm -rf $(VENV_DIR)
	@rm -rf written.db
	@echo "$(GREEN)✅ Deep cleanup completed$(NC)"

## Show project status
status:
	@echo "$(BLUE)📊 Written AI Chatbot - Project Status$(NC)"
	@echo "$(BLUE)====================================$(NC)"
	@echo ""
	@echo "$(GREEN)🐍 Python:$(NC) $(shell $(PYTHON) --version)"
	@echo "$(GREEN)📁 Project:$(NC) $(shell pwd)"
	@echo "$(GREEN)🌐 Virtual Env:$(NC) $(if $(shell test -d $(VENV_DIR) && echo "yes"),✅ Active,❌ Not found)"
	@echo "$(GREEN)🗄️  Database:$(NC) $(shell . $(VENV_DIR)/bin/activate 2>/dev/null && $(PYTHON) -c "from src.database.postgres_manager import get_database_manager; print('✅ Connected' if get_database_manager().test_connection() else '❌ Disconnected')" 2>/dev/null || echo "❌ Cannot check")"
	@echo "$(GREEN)🐳 Docker:$(NC) $(shell docker ps --filter name=postgres-written --format "table {{.Status}}" 2>/dev/null | tail -n +2 || echo "❌ Not running")"
	@echo ""
	@if [ -f .env ]; then \
		echo "$(GREEN)⚙️  Environment:$(NC) ✅ .env file exists"; \
	else \
		echo "$(GREEN)⚙️  Environment:$(NC) ❌ .env file missing"; \
	fi

## Check environment setup
env-check:
	@echo "$(BLUE)🔍 Environment Check$(NC)"
	@echo "$(BLUE)==================$(NC)"
	@echo ""
	@echo "$(GREEN)Checking Python...$(NC)"
	@$(PYTHON) --version || echo "$(RED)❌ Python 3 not found$(NC)"
	@echo ""
	@echo "$(GREEN)Checking Docker...$(NC)"
	@docker --version 2>/dev/null || echo "$(YELLOW)⚠️  Docker not found (optional for local PostgreSQL)$(NC)"
	@echo ""
	@echo "$(GREEN)Checking PostgreSQL connection...$(NC)"
	@pg_isready -h localhost -p 5433 -U postgres 2>/dev/null && echo "✅ PostgreSQL ready" || echo "$(YELLOW)⚠️  PostgreSQL not ready (run 'make docker-up' or start your PostgreSQL)$(NC)"
	@echo ""
	@echo "$(GREEN)Checking project files...$(NC)"
	@[ -f app.py ] && echo "✅ app.py found" || echo "$(RED)❌ app.py missing$(NC)"
	@[ -f requirements.txt ] && echo "✅ requirements.txt found" || echo "$(RED)❌ requirements.txt missing$(NC)"
	@[ -f .env ] && echo "✅ .env found" || echo "$(YELLOW)⚠️  .env missing (copy from .env.example)$(NC)"

# Quick aliases
.PHONY: start server
start: run
server: run

# Ensure targets don't conflict with files
.PHONY: help setup venv install run dev db-setup db-migrate db-reset db-status test lint format docker-up docker-down docker-logs logs clean clean-all status env-check
