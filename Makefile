.PHONY: help install dev up down logs clean test lint format migrate init

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with UV
	uv sync

dev: ## Start development server
	uv run uvicorn services.api_gateway.main:app --reload --port 8086

up: ## Start Docker services
	docker-compose up -d

down: ## Stop Docker services
	docker-compose down

logs: ## Show Docker logs
	docker-compose logs -f

clean: ## Clean Docker volumes and stop services
	docker-compose down -v

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=services --cov-report=html --cov-report=term

lint: ## Run linting
	uv run ruff check services/ tests/

format: ## Format code
	uv run black services/ tests/
	uv run ruff check --fix services/ tests/

type-check: ## Run type checking
	uv run mypy services/

migrate: ## Run database migrations
	uv run alembic upgrade head

migrate-create: ## Create new migration (use MSG="description")
	uv run alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback last migration
	uv run alembic downgrade -1

init: ## Initialize development environment
	./scripts/init.sh

seed: ## Seed database with test data
	uv run python scripts/seed_db.py

test-api: ## Test API endpoints
	uv run python scripts/test_api.py

db-shell: ## Open PostgreSQL shell
	docker exec -it bsmart-postgres psql -U bsmart -d bsmart_alm

redis-cli: ## Open Redis CLI
	docker exec -it bsmart-redis redis-cli

rabbitmq-shell: ## Open RabbitMQ management
	@echo "Opening RabbitMQ Management UI at http://localhost:15672"
	@echo "Username: guest"
	@echo "Password: guest"

minio-console: ## Open MinIO console
	@echo "Opening MinIO Console at http://localhost:9001"
	@echo "Username: minioadmin"
	@echo "Password: minioadmin"

ollama-pull: ## Pull Ollama model
	docker exec bsmart-ollama ollama pull llama3.2

ollama-list: ## List Ollama models
	docker exec bsmart-ollama ollama list

docker-rebuild: ## Rebuild Docker services
	docker-compose build --no-cache
	docker-compose up -d
