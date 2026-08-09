# ==========================================
# Website2Video AI - Makefile
# ==========================================

SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Project variables
PROJECT_NAME := website2video
COMPOSE_FILE := docker-compose.yml
COMPOSE_PROFILES := --profile monitoring --profile logging
PYTHON := python3
POETRY := poetry
PNPM := pnpm
NODE := node

# Environment variables
ENV_FILE := .env
-include $(ENV_FILE)
export $(shell sed 's/=.*//' $(ENV_FILE))

# ==========================================
# HELP
# ==========================================
.PHONY: help
help: ## Show this help message
	@echo '$(BLUE)Website2Video AI - Makefile Commands$(NC)'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-30s$(NC) %s\n", $$1, $$2}'
	@echo ''

# ==========================================
# DEVELOPMENT
# ==========================================
.PHONY: dev
dev: ## Start development environment
	@echo '$(BLUE)Starting development environment...$(NC)'
	@make up
	@echo '$(GREEN)✓ Development environment started$(NC)'
	@echo '  Frontend: http://localhost:5173'
	@echo '  Backend API: http://localhost:8000'
	@echo '  API Docs: http://localhost:8000/docs'
	@echo '  Flower: http://localhost:5555'
	@echo '  MinIO: http://localhost:9001'
	@echo '  $(YELLOW)Press Ctrl+C to stop$(NC)'
	@docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: dev-backend
dev-backend: ## Start only backend services
	@echo '$(BLUE)Starting backend services...$(NC)'
	@docker-compose -f $(COMPOSE_FILE) up -d postgres redis minio backend worker beat
	@echo '$(GREEN)✓ Backend services started$(NC)'
	@docker-compose -f $(COMPOSE_FILE) logs -f backend worker

.PHONY: dev-frontend
dev-frontend: ## Start only frontend services
	@echo '$(BLUE)Starting frontend services...$(NC)'
	@docker-compose -f $(COMPOSE_FILE) up -d frontend
	@echo '$(GREEN)✓ Frontend services started$(NC)'
	@docker-compose -f $(COMPOSE_FILE) logs -f frontend

# ==========================================
# DOCKER COMPOSE
# ==========================================
.PHONY: up
up: ## Start all services
	@echo '$(BLUE)Starting all services...$(NC)'
	@docker-compose -f $(COMPOSE_FILE) $(COMPOSE_PROFILES) up -d
	@echo '$(GREEN)✓ All services started$(NC)'
	@make status

.PHONY: down
down: ## Stop all services
	@echo '$(BLUE)Stopping all services...$(NC)'
	@docker-compose -f $(COMPOSE_FILE) down
	@echo '$(GREEN)✓ All services stopped$(NC)'

.PHONY: down-clean
down-clean: ## Stop and remove all containers, volumes, and networks
	@echo '$(RED)WARNING: This will delete all data volumes!$(NC)'
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo ''; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f $(COMPOSE_FILE) down -v --rmi all --remove-orphans; \
		echo '$(GREEN)✓ Cleanup complete$(NC)'; \
	else \
		echo '$(YELLOW)Aborted$(NC)'; \
	fi

.PHONY: restart
restart: ## Restart all services
	@echo '$(BLUE)Restarting services...$(NC)'
	@make down
	@make up
	@echo '$(GREEN)✓ Services restarted$(NC)'

.PHONY: logs
logs: ## View all logs
	@docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: logs-backend
logs-backend: ## View backend logs
	@docker-compose -f $(COMPOSE_FILE) logs -f backend

.PHONY: logs-worker
logs-worker: ## View worker logs
	@docker-compose -f $(COMPOSE_FILE) logs -f worker

.PHONY: logs-frontend
logs-frontend: ## View frontend logs
	@docker-compose -f $(COMPOSE_FILE) logs -f frontend

.PHONY: status
status: ## Show service status
	@echo '$(BLUE)Service Status:$(NC)'
	@docker-compose -f $(COMPOSE_FILE) ps

.PHONY: ps
ps: status ## Alias for status

# ==========================================
# BUILD
# ==========================================
.PHONY: build
build: ## Build all Docker images
	@echo '$(BLUE)Building Docker images...$(NC)'
	@docker-compose -f $(COMPOSE_FILE) build --parallel
	@echo '$(GREEN)✓ Build complete$(NC)'

.PHONY: build-backend
build-backend: ## Build backend Docker image
	@echo '$(BLUE)Building backend image...$(NC)'
	@docker-compose -f $(COMPOSE_FILE) build backend
	@echo '$(GREEN)✓ Backend build complete$(NC)'

.PHONY: build-frontend
build-frontend: ## Build frontend Docker image
	@echo '$(BLUE)Building frontend image...$(NC)'
	@docker-compose -f $(COMPOSE_FILE) build frontend
	@echo '$(GREEN)✓ Frontend build complete$(NC)'

.PHONY: build-production
build-production: ## Build production images
	@echo '$(BLUE)Building production images...$(NC)'
	@docker-compose -f $(COMPOSE_FILE) -f docker-compose.prod.yml build
	@echo '$(GREEN)✓ Production build complete$(NC)'

# ==========================================
# BACKEND (Local)
# ==========================================
.PHONY: backend-install
backend-install: ## Install backend dependencies
	@echo '$(BLUE)Installing backend dependencies...$(NC)'
	@cd backend && $(POETRY) install
	@echo '$(GREEN)✓ Backend dependencies installed$(NC)'

.PHONY: backend-lint
backend-lint: ## Lint backend code
	@echo '$(BLUE)Linting backend code...$(NC)'
	@cd backend && $(POETRY) run black --check app/
	@cd backend && $(POETRY) run isort --check-only app/
	@cd backend && $(POETRY) run flake8 app/ --count --max-complexity=10 --max-line-length=127 --statistics
	@cd backend && $(POETRY) run mypy app/ --ignore-missing-imports
	@echo '$(GREEN)✓ Linting complete$(NC)'

.PHONY: backend-format
backend-format: ## Format backend code
	@echo '$(BLUE)Formatting backend code...$(NC)'
	@cd backend && $(POETRY) run black app/
	@cd backend && $(POETRY) run isort app/
	@echo '$(GREEN)✓ Formatting complete$(NC)'

.PHONY: backend-test
backend-test: ## Run backend tests
	@echo '$(BLUE)Running backend tests...$(NC)'
	@cd backend && $(POETRY) run pytest tests/ -v --cov=app --cov-report=html --cov-report=term
	@echo '$(GREEN)✓ Tests complete$(NC)'

.PHONY: backend-test-coverage
backend-test-coverage: ## Run backend tests with coverage report
	@cd backend && $(POETRY) run pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
	@echo '$(GREEN)✓ Coverage report generated at backend/htmlcov/index.html$(NC)'

.PHONY: backend-clean
backend-clean: ## Clean backend cache files
	@echo '$(BLUE)Cleaning backend cache...$(NC)'
	@cd backend && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@cd backend && find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@cd backend && find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@cd backend && find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@cd backend && find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf backend/htmlcov backend/coverage.xml 2>/dev/null || true
	@echo '$(GREEN)✓ Backend cleaned$(NC)'

.PHONY: backend-shell
backend-shell: ## Open backend Python shell
	@cd backend && $(POETRY) run python

# ==========================================
# FRONTEND (Local)
# ==========================================
.PHONY: frontend-install
frontend-install: ## Install frontend dependencies
	@echo '$(BLUE)Installing frontend dependencies...$(NC)'
	@cd frontend && $(PNPM) install
	@echo '$(GREEN)✓ Frontend dependencies installed$(NC)'

.PHONY: frontend-lint
frontend-lint: ## Lint frontend code
	@echo '$(BLUE)Linting frontend code...$(NC)'
