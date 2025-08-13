.PHONY: help install dev test clean build up down logs

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create virtual environment
	@command -v uv >/dev/null 2>&1 || { echo "❌ UV not found. Install with: pip install uv"; exit 1; }
	@if [ ! -d ".venv" ]; then \
		echo "🐍 Creating virtual environment..."; \
		uv venv; \
		echo "✅ Virtual environment created at .venv/"; \
	else \
		echo "✅ Virtual environment already exists"; \
	fi

setup: ## Complete setup (create venv + install all dependencies)
	@echo "🚀 Setting up development environment..."
	@command -v uv >/dev/null 2>&1 || { echo "📦 Installing UV..."; pip install uv; }
	@$(MAKE) venv
	@echo "📚 Installing dependencies..."
	uv pip install -e .
	@echo "🛠️ Installing development tools..."
	uv pip install -e ".[dev]"
	@echo "✅ Setup complete!"
	@echo "💡 To activate venv: source .venv/bin/activate"
	@echo "💡 Or prefix commands with: uv run <command>"

install: ## Install dependencies (requires venv or --system flag)
	@command -v uv >/dev/null 2>&1 || { echo "❌ UV not found. Install with: pip install uv"; exit 1; }
	@if [ ! -d ".venv" ] && [ "$(SYSTEM)" != "true" ]; then \
		echo "❌ No virtual environment found."; \
		echo "💡 Run: make venv  OR  make SYSTEM=true install"; \
		exit 1; \
	fi
	uv pip install -e .

dev: ## Install development dependencies (requires venv or --system flag)
	@command -v uv >/dev/null 2>&1 || { echo "❌ UV not found. Install with: pip install uv"; exit 1; }
	@if [ ! -d ".venv" ] && [ "$(SYSTEM)" != "true" ]; then \
		echo "❌ No virtual environment found."; \
		echo "💡 Run: make setup  OR  make SYSTEM=true dev"; \
		exit 1; \
	fi
	uv pip install -e ".[dev]"

test: ## Run all tests (auto-detects venv)
	@if [ -d ".venv" ]; then \
		echo "🧪 Running all tests in virtual environment..."; \
		uv run pytest --cov=app --cov-report=html --cov-report=term-missing; \
	else \
		echo "🧪 Running all tests in system environment..."; \
		command -v pytest >/dev/null 2>&1 || { echo "❌ Pytest not found. Run: make setup"; exit 1; }; \
		pytest --cov=app --cov-report=html --cov-report=term-missing; \
	fi

test-unit: ## Run unit tests only (auto-detects venv)
	@if [ -d ".venv" ]; then \
		echo "🧪 Running unit tests in virtual environment..."; \
		uv run pytest tests/ -k "not integration" --cov=app --cov-report=html --cov-report=term-missing; \
	else \
		echo "🧪 Running unit tests in system environment..."; \
		command -v pytest >/dev/null 2>&1 || { echo "❌ Pytest not found. Run: make setup"; exit 1; }; \
		pytest tests/ -k "not integration" --cov=app --cov-report=html --cov-report=term-missing; \
	fi

test-integration: ## Run integration tests only (auto-detects venv)
	@if [ -d ".venv" ]; then \
		echo "🧪 Running integration tests in virtual environment..."; \
		uv run pytest tests/integration/ --cov=app --cov-report=html --cov-report=term-missing; \
	else \
		echo "🧪 Running integration tests in system environment..."; \
		command -v pytest >/dev/null 2>&1 || { echo "❌ Pytest not found. Run: make setup"; exit 1; }; \
		pytest tests/integration/ --cov=app --cov-report=html --cov-report=term-missing; \
	fi

test-watch: ## Run tests in watch mode
	@if [ -d ".venv" ]; then \
		uv run pytest-watch; \
	else \
		command -v pytest-watch >/dev/null 2>&1 || { echo "❌ Pytest-watch not found. Install with: pip install pytest-watch"; exit 1; }; \
		pytest-watch; \
	fi

lint: ## Run linting (auto-detects venv)
	@echo "🔍 Running linting checks..."
	@if [ -d ".venv" ]; then \
		echo "Using virtual environment..."; \
		uv run black --check app tests; \
		uv run ruff check app tests; \
		uv run ruff format app tests --check; \
		uv run mypy app --ignore-missing-imports --disable-error-code=var-annotated --disable-error-code=arg-type; \
	else \
		command -v black >/dev/null 2>&1 || { echo "❌ Black not found. Run: make setup"; exit 1; }; \
		command -v ruff >/dev/null 2>&1 || { echo "❌ Ruff not found. Run: make setup"; exit 1; }; \
		command -v mypy >/dev/null 2>&1 || { echo "❌ MyPy not found. Run: make setup"; exit 1; }; \
		black --check app tests; \
		ruff check app tests; \
		ruff format app tests --check; \
		mypy app --ignore-missing-imports --disable-error-code=var-annotated --disable-error-code=arg-type; \
	fi
	@echo "✅ All linting checks passed!"

format: ## Format code (auto-detects venv)
	@echo "🎨 Formatting code..."
	@if [ -d ".venv" ]; then \
		uv run black app tests; \
		uv run ruff format app tests; \
		uv run ruff check app tests --fix; \
	else \
		command -v black >/dev/null 2>&1 || { echo "❌ Black not found. Run: make setup"; exit 1; }; \
		command -v ruff >/dev/null 2>&1 || { echo "❌ Ruff not found. Run: make setup"; exit 1; }; \
		black app tests; \
		ruff format app tests; \
		ruff check app tests --fix; \
	fi
	@echo "✅ Code formatted!"

security: ## Run security checks (auto-detects venv)
	@if [ -d ".venv" ]; then \
		uv run bandit -r app/; \
		uv run safety check; \
	else \
		command -v bandit >/dev/null 2>&1 || { echo "❌ Bandit not found. Run: make setup"; exit 1; }; \
		command -v safety >/dev/null 2>&1 || { echo "❌ Safety not found. Run: make setup"; exit 1; }; \
		bandit -r app/; \
		safety check; \
	fi

clean-cache: ## Clean up only cache files and temporary data
	@echo "🧹 Cleaning up cache files and temporary data..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -rf .coverage htmlcov/ .pytest_cache/
	@rm -rf .mypy_cache/ .ruff_cache/
	@rm -rf *.db test*.db
	@rm -rf .tmp/ tmp/
	@rm -rf *.log logs/
	@find . -name "*.tmp" -delete
	@find . -name "*.temp" -delete
	@find . -name "*.bak" -delete
	@find . -name ".DS_Store" -delete
	@echo "✅ Cache cleanup completed!"

clean: clean-cache ## Complete cleanup (cache + venv)
	@echo "🗑️ Removing virtual environment..."
	@rm -rf .venv
	@echo "✅ Complete cleanup finished!"

clean-venv: ## Remove only virtual environment
	@if [ -d ".venv" ]; then \
		echo "🗑️ Removing virtual environment..."; \
		rm -rf .venv; \
		echo "✅ Virtual environment removed"; \
	else \
		echo "❌ No virtual environment found"; \
	fi

build: ## Build Docker images
	docker-compose build

up: ## Start services
	docker-compose up -d

down: ## Stop services
	docker-compose down

logs: ## Show logs
	docker-compose logs -f

setup-db: ## Setup database with migrations
	alembic upgrade head

migration: ## Create new migration
	alembic revision --autogenerate -m "$(name)"

run-dev: ## Run development server
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-consumer: ## Run RabbitMQ consumer
	python app/consumers/task_consumer.py

frontend-dev: ## Run frontend in development mode
	cd frontend && npm start

frontend-install: ## Install frontend dependencies
	cd frontend && npm install

frontend-build: ## Build frontend for production
	cd frontend && npm run build
