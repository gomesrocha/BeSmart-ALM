# Quick Start Guide

Get Bsmart-ALM up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ installed
- UV package manager (optional but recommended)

## Step 1: Clone and Setup

```bash
# Navigate to project directory
cd bsmart-alm

# Copy environment file
cp .env.example .env
```

## Step 2: Initialize Environment

### Option A: Using the init script (Recommended)

```bash
# Make script executable and run
chmod +x scripts/init.sh
./scripts/init.sh
```

This script will:
- Start all Docker services (PostgreSQL, RabbitMQ, MinIO, Redis, Ollama)
- Wait for services to be healthy
- Pull the Ollama llama3.2 model
- Enable pgvector extension
- Create MinIO bucket

### Option B: Manual setup

```bash
# Start Docker services
docker-compose up -d

# Wait for services to be ready (check with docker-compose ps)

# Pull Ollama model
docker exec bsmart-ollama ollama pull llama3.2

# Enable pgvector
docker exec bsmart-postgres psql -U bsmart -d bsmart_alm -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Step 3: Install Dependencies

### With UV (Recommended)

```bash
uv sync
```

### With pip

```bash
pip install -e ".[dev]"
```

## Step 4: Run Database Migrations

```bash
# With UV
uv run alembic upgrade head

# With python
python -m alembic upgrade head
```

## Step 5: Start the API Server

```bash
# With UV
uv run uvicorn services.api_gateway.main:app --reload --port 8000

# With python
python -m uvicorn services.api_gateway.main:app --reload --port 8000

# Or using make
make dev
```

## Step 6: Verify Installation

Open your browser and visit:

- **API Documentation**: http://localhost:8000/docs
- **API Root**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

You should see the Swagger UI with API documentation!

## Service Access

### RabbitMQ Management
- URL: http://localhost:15672
- Username: `guest`
- Password: `guest`

### MinIO Console
- URL: http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin`

### PostgreSQL
```bash
# Connect via docker
docker exec -it bsmart-postgres psql -U bsmart -d bsmart_alm

# Or via make
make db-shell
```

### Redis
```bash
# Connect via docker
docker exec -it bsmart-redis redis-cli

# Or via make
make redis-cli
```

## Common Commands

```bash
# Start services
make up

# Stop services
make down

# View logs
make logs

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Create migration
make migrate-create MSG="your migration description"

# Apply migrations
make migrate

# See all available commands
make help
```

## Troubleshooting

### Services not starting

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs

# Restart services
docker-compose restart
```

### Database connection issues

```bash
# Check PostgreSQL is running
docker exec bsmart-postgres pg_isready -U bsmart

# Verify connection
docker exec -it bsmart-postgres psql -U bsmart -d bsmart_alm -c "SELECT 1;"
```

### Ollama model not found

```bash
# Pull the model manually
docker exec bsmart-ollama ollama pull llama3.2

# Verify model is available
docker exec bsmart-ollama ollama list
```

### Port conflicts

If you have port conflicts, edit `docker-compose.yml` to change the port mappings:

```yaml
ports:
  - "5433:5432"  # Change 5432 to 5433 for PostgreSQL
```

## Next Steps

1. Read the [README.md](README.md) for detailed documentation
2. Check the [design document](.kiro/specs/bsmart-alm-platform/design.md) for architecture details
3. Review the [requirements](.kiro/specs/bsmart-alm-platform/requirements.md)
4. Start implementing tasks from [tasks.md](.kiro/specs/bsmart-alm-platform/tasks.md)

## Development Workflow

1. Create a feature branch
2. Implement your changes
3. Run tests: `make test`
4. Format code: `make format`
5. Run linting: `make lint`
6. Commit and push
7. Create a pull request

Happy coding! 🚀
