.PHONY: help dev-up dev-down dev-build dev-logs dev-shell dev-migrate dev-test dev-restart dev-clean prod-up prod-down prod-build prod-logs prod-clean

# Default target when just running 'make'
.DEFAULT_GOAL := help

# ANSI color codes for better output
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Don't export color codes to subprocesses (prevents docker-compose warnings)
unexport GREEN YELLOW BLUE NC

##@ Help

help: ## Display this help message
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(GREEN)  NoteApp Docker Commands$(NC)"
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(GREEN)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

##@ Development

dev-up: ## Start development environment
	@echo "$(GREEN)Starting development environment...$(NC)"
	docker-compose -f docker-compose.dev.yml up

dev-up-d: ## Start development environment in detached mode
	@echo "$(GREEN)Starting development environment in detached mode...$(NC)"
	docker-compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✓ Development environment started!$(NC)"
	@echo "$(BLUE)API:$(NC) http://localhost:8000"
	@echo "$(BLUE)Docs:$(NC) http://localhost:8000/api/docs/"

dev-down: ## Stop development environment
	@echo "$(YELLOW)Stopping development environment...$(NC)"
	docker-compose -f docker-compose.dev.yml down

dev-build: ## Build/rebuild development containers
	@echo "$(GREEN)Building development containers...$(NC)"
	docker-compose -f docker-compose.dev.yml build

dev-rebuild: ## Rebuild development containers without cache
	@echo "$(GREEN)Rebuilding development containers from scratch...$(NC)"
	docker-compose -f docker-compose.dev.yml build --no-cache

dev-logs: ## View development logs (all services)
	docker-compose -f docker-compose.dev.yml logs -f

dev-logs-api: ## View API service logs only
	docker-compose -f docker-compose.dev.yml logs -f api

dev-logs-celery: ## View Celery worker logs only
	docker-compose -f docker-compose.dev.yml logs -f celery_worker

dev-shell: ## Access Django shell in API container
	docker-compose -f docker-compose.dev.yml exec api python manage.py shell

dev-bash: ## Access bash shell in API container
	docker-compose -f docker-compose.dev.yml exec api bash

dev-migrate: ## Run database migrations
	docker-compose -f docker-compose.dev.yml exec api python manage.py migrate

dev-makemigrations: ## Create new migrations
	docker-compose -f docker-compose.dev.yml exec api python manage.py makemigrations

dev-test: ## Run tests
	docker-compose -f docker-compose.dev.yml exec api pytest

dev-test-cov: ## Run tests with coverage report
	docker-compose -f docker-compose.dev.yml exec api pytest --cov=apps --cov-report=html --cov-report=term

dev-lint: ## Run code linters (black, ruff)
	docker-compose -f docker-compose.dev.yml exec api black --check .
	docker-compose -f docker-compose.dev.yml exec api ruff check .

dev-format: ## Format code with black
	docker-compose -f docker-compose.dev.yml exec api black .

dev-restart: ## Restart all development services
	@echo "$(YELLOW)Restarting development services...$(NC)"
	docker-compose -f docker-compose.dev.yml restart

dev-restart-api: ## Restart API service only
	docker-compose -f docker-compose.dev.yml restart api

dev-restart-celery: ## Restart Celery worker only
	docker-compose -f docker-compose.dev.yml restart celery_worker

dev-clean: ## Stop and remove all development containers, volumes, and images
	@echo "$(YELLOW)Cleaning up development environment...$(NC)"
	docker-compose -f docker-compose.dev.yml down -v --rmi local
	@echo "$(GREEN)✓ Development environment cleaned!$(NC)"

dev-ps: ## Show status of development containers
	docker-compose -f docker-compose.dev.yml ps

##@ Production

prod-up: ## Start production environment
	@echo "$(GREEN)Starting production environment...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Production environment started!$(NC)"

prod-down: ## Stop production environment
	@echo "$(YELLOW)Stopping production environment...$(NC)"
	docker-compose down

prod-build: ## Build/rebuild production containers
	@echo "$(GREEN)Building production containers...$(NC)"
	docker-compose build

prod-rebuild: ## Rebuild production containers without cache
	@echo "$(GREEN)Rebuilding production containers from scratch...$(NC)"
	docker-compose build --no-cache

prod-logs: ## View production logs (all services)
	docker-compose logs -f

prod-logs-api: ## View API service logs only
	docker-compose logs -f api

prod-logs-celery: ## View Celery worker logs only
	docker-compose logs -f celery_worker

prod-shell: ## Access Django shell in production API container
	docker-compose exec api python manage.py shell

prod-bash: ## Access bash shell in production API container
	docker-compose exec api bash

prod-migrate: ## Run database migrations in production
	docker-compose exec api python manage.py migrate

prod-ps: ## Show status of production containers
	docker-compose ps

prod-clean: ## Stop and remove all production containers and volumes
	@echo "$(YELLOW)Cleaning up production environment...$(NC)"
	docker-compose down -v
	@echo "$(GREEN)✓ Production environment cleaned!$(NC)"

##@ Database

db-backup: ## Backup development database
	@echo "$(GREEN)Creating database backup...$(NC)"
	docker-compose -f docker-compose.dev.yml exec -T postgres pg_dump -U noteapp_user noteapp_db > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Database backup created!$(NC)"

db-restore: ## Restore development database (use: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)Usage: make db-restore FILE=backup.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Restoring database from $(FILE)...$(NC)"
	docker-compose -f docker-compose.dev.yml exec -T postgres psql -U noteapp_user noteapp_db < $(FILE)
	@echo "$(GREEN)✓ Database restored!$(NC)"
