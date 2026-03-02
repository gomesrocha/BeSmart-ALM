#!/bin/bash
set -e

echo "🚀 Initializing Bsmart-ALM Development Environment"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Start Docker services
echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check PostgreSQL
echo "Checking PostgreSQL..."
until docker exec bsmart-postgres pg_isready -U bsmart > /dev/null 2>&1; do
    echo "  Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Check RabbitMQ
echo "Checking RabbitMQ..."
until docker exec bsmart-rabbitmq rabbitmq-diagnostics ping > /dev/null 2>&1; do
    echo "  Waiting for RabbitMQ..."
    sleep 2
done
echo "✅ RabbitMQ is ready"

# Check MinIO
echo "Checking MinIO..."
until curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; do
    echo "  Waiting for MinIO..."
    sleep 2
done
echo "✅ MinIO is ready"

# Check Redis
echo "Checking Redis..."
until docker exec bsmart-redis redis-cli ping > /dev/null 2>&1; do
    echo "  Waiting for Redis..."
    sleep 2
done
echo "✅ Redis is ready"

# Check Ollama
echo "Checking Ollama..."
until curl -f http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "  Waiting for Ollama..."
    sleep 2
done
echo "✅ Ollama is ready"

# Pull Ollama model
echo ""
echo "📥 Pulling Ollama llama3.2 model (this may take a while)..."
docker exec bsmart-ollama ollama pull llama3.2
echo "✅ Ollama model ready"

# Enable pgvector extension
echo ""
echo "🔧 Enabling pgvector extension..."
docker exec bsmart-postgres psql -U bsmart -d bsmart_alm -c "CREATE EXTENSION IF NOT EXISTS vector;" > /dev/null 2>&1
echo "✅ pgvector extension enabled"

# Create MinIO bucket
echo ""
echo "🪣 Creating MinIO bucket..."
docker run --rm --network bsmart-alm_bsmart-network \
    -e MC_HOST_minio=http://minioadmin:minioadmin@minio:9000 \
    minio/mc mb minio/bsmart-alm --ignore-existing > /dev/null 2>&1 || true
echo "✅ MinIO bucket created"

echo ""
echo "✨ Development environment is ready!"
echo ""
echo "📚 Next steps:"
echo "  1. Install dependencies: uv sync"
echo "  2. Run migrations: uv run alembic upgrade head"
echo "  3. Start API server: uv run uvicorn services.api_gateway.main:app --reload"
echo ""
echo "🌐 Service URLs:"
echo "  - API Gateway: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - RabbitMQ Management: http://localhost:15672 (guest/guest)"
echo "  - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo ""
