# Bsmart-ALM

AI-first Application Lifecycle Management platform with MPS.BR compliance support.

## Overview

Bsmart-ALM is a modular, AI-powered platform for managing the complete software development lifecycle. It integrates with existing tools (Jira, Azure DevOps, Git, IDEs) and provides intelligent assistance across all phases: Requirements, Analysis, Code, Review, Testing, Security, and Management.

### Key Features

- **AI-First**: Powered by Ollama (llama-3.2) with RAG for context-aware assistance
- **Multi-Tenant**: Complete tenant isolation with RBAC
- **MPS.BR Compliance**: Automated evidence collection and audit trails
- **Modular Architecture**: Microservices-based with event-driven communication
- **Integrations**: Jira, Azure DevOps, Git, CI/CD pipelines
- **Quality Gates**: Automated validation at every stage

## Technology Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: PostgreSQL 16 + pgvector
- **Message Queue**: RabbitMQ
- **Object Storage**: MinIO (dev), S3-compatible (prod)
- **LLM**: Ollama (llama-3.2)
- **Cache**: Redis
- **Container**: Docker
- **Orchestration**: Kubernetes (production)

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- UV package manager (recommended)

## Quick Start

### 1. Install UV (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### 2. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd bsmart-alm

# Copy environment file
cp .env.example .env

# Install dependencies with UV
uv sync

# Or with pip
pip install -e ".[dev]"
```

### 3. Start Infrastructure Services

```bash
# Start all services (PostgreSQL, RabbitMQ, MinIO, Redis, Ollama)
docker-compose up -d

# Check services are healthy
docker-compose ps

# Pull Ollama model (first time only)
docker exec -it bsmart-ollama ollama pull llama3.2
```

### 4. Initialize Database

```bash
# Run migrations
uv run alembic upgrade head

# Or with python
python -m alembic upgrade head
```

### 5. Run Development Server

```bash
# Start API server
uv run uvicorn services.api_gateway.main:app --reload --port 8000

# Or with python
python -m uvicorn services.api_gateway.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Project Structure

```
bsmart-alm/
├── services/
│   ├── shared/              # Shared utilities and models
│   │   ├── config.py        # Configuration management
│   │   ├── database.py      # Database connection
│   │   └── models/          # Shared data models
│   ├── identity/            # Identity & Tenant Service
│   ├── project/             # Project Service
│   ├── work_item/           # Work Item Service
│   ├── ai_orchestrator/     # AI Orchestration Service
│   ├── rag/                 # RAG Service
│   ├── requirements/        # Requirements Module
│   ├── analysis/            # Analysis Module
│   ├── code/                # Code Module
│   ├── review/              # Review Module
│   ├── testing/             # Testing Module
│   ├── security/            # Security Module
│   ├── management/          # Management Module
│   ├── integration/         # Integration Hub
│   └── api_gateway/         # API Gateway
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── docker-compose.yml       # Local development infrastructure
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=services --cov-report=html

# Run specific test file
uv run pytest tests/test_identity.py
```

### Code Quality

```bash
# Format code
uv run black services/ tests/

# Lint code
uv run ruff check services/ tests/

# Type checking
uv run mypy services/
```

### Database Migrations

```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## Service URLs (Development)

- **API Gateway**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **Redis**: localhost:6379
- **Ollama**: http://localhost:11434

## Architecture

The platform follows a microservices architecture with:

- **Core Services**: Identity, Project, Work Item, Artifact, Audit, Policy
- **AI Services**: Orchestrator, RAG, Prompt Registry
- **Module Services**: Requirements, Analysis, Code, Review, Testing, Security, Management
- **Integration Layer**: Jira, Azure DevOps, Git adapters
- **Infrastructure**: PostgreSQL, RabbitMQ, MinIO, Redis, Ollama

See [design.md](.kiro/specs/bsmart-alm-platform/design.md) for detailed architecture documentation.

## MPS.BR Compliance

The platform automatically collects evidence for MPS.BR processes:

- **GRE** (Gerência de Requisitos): Requirements traceability and versioning
- **GPR** (Gerência de Projetos): Project planning and tracking
- **MED** (Medição): Automated metrics collection
- **GQA** (Garantia da Qualidade): Quality gates and checklists
- **GCO** (Gerência de Configuração): Git integration and baselines
- **VER** (Verificação): Code review and testing evidence
- **VAL** (Validação): Acceptance criteria validation

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and quality checks
4. Submit a pull request

## License

[To be defined]

## Support

For issues and questions, please open an issue in the repository.
