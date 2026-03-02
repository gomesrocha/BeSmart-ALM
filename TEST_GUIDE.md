# Test Guide - Bsmart-ALM

Guia rápido para testar a aplicação.

## Pré-requisitos

1. Docker Compose rodando (PostgreSQL, RabbitMQ, MinIO, Redis)
2. Ollama rodando localmente na porta 11434
3. Dependências instaladas com `uv sync`

## Passo 1: Iniciar Serviços Docker

```bash
# Iniciar serviços (sem Ollama, pois você já tem local)
docker-compose up -d

# Verificar se estão rodando
docker-compose ps
```

## Passo 2: Criar Migração e Aplicar

```bash
# Criar migração inicial
uv run alembic revision --autogenerate -m "initial migration"

# Aplicar migração
uv run alembic upgrade head
```

## Passo 3: Popular Banco com Dados de Teste

```bash
# Executar seed
make seed

# Ou diretamente
uv run python scripts/seed_db.py
```

Isso criará:
- 1 tenant: "Test Organization"
- 6 roles padrão: admin, po, dev, qa, sec, auditor
- 3 usuários:
  - **admin@test.com** / admin123456 (superuser)
  - **dev@test.com** / dev123456
  - **po@test.com** / po123456

## Passo 4: Iniciar Servidor

```bash
# Iniciar servidor na porta 8086
make dev

# Ou diretamente
uv run uvicorn services.api_gateway.main:app --reload --port 8086
```

## Passo 5: Testar API

### Opção A: Script Automatizado

```bash
# Executar testes automatizados
make test-api

# Ou diretamente
uv run python scripts/test_api.py
```

### Opção B: Swagger UI

Abra no navegador: http://localhost:8086/docs

### Opção C: cURL Manual

```bash
# 1. Login
curl -X POST http://localhost:8086/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123456"}'

# Copie o access_token da resposta

# 2. Get user info
curl -X GET http://localhost:8086/api/v1/auth/me \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"

# 3. List roles
curl -X GET http://localhost:8086/api/v1/roles \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"

# 4. Create API token
curl -X POST http://localhost:8086/api/v1/api-tokens \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Token","scopes":["project:read"],"expires_in_days":30}'
```

## Endpoints Disponíveis

### Autenticação
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/token/refresh` - Refresh token
- `GET /api/v1/auth/me` - User info
- `POST /api/v1/auth/logout` - Logout

### Roles (requer permissão admin)
- `GET /api/v1/roles` - List roles
- `GET /api/v1/roles/{id}` - Get role
- `POST /api/v1/roles` - Create role
- `PATCH /api/v1/roles/{id}` - Update role
- `DELETE /api/v1/roles/{id}` - Delete role
- `POST /api/v1/roles/{role_id}/assign/{user_id}` - Assign role
- `DELETE /api/v1/roles/{role_id}/unassign/{user_id}` - Unassign role

### API Tokens
- `GET /api/v1/api-tokens` - List tokens
- `POST /api/v1/api-tokens` - Create token
- `GET /api/v1/api-tokens/{id}` - Get token
- `PATCH /api/v1/api-tokens/{id}/revoke` - Revoke token
- `DELETE /api/v1/api-tokens/{id}` - Delete token

## Verificar Logs

```bash
# Logs do servidor (se rodando via make dev)
# Ctrl+C para parar

# Logs do Docker
docker-compose logs -f

# Logs específicos
docker-compose logs postgres
docker-compose logs rabbitmq
```

## Troubleshooting

### Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Verificar logs
docker-compose logs postgres

# Reiniciar
docker-compose restart postgres
```

### Erro de migração

```bash
# Resetar banco (CUIDADO: apaga todos os dados)
docker-compose down -v
docker-compose up -d

# Recriar migração
rm -rf alembic/versions/*.py
uv run alembic revision --autogenerate -m "initial migration"
uv run alembic upgrade head
```

### Porta 8086 em uso

```bash
# Verificar o que está usando a porta
lsof -i :8086

# Ou mudar a porta no Makefile e services/api_gateway/main.py
```

## Próximos Passos

Após testar com sucesso:

1. Implementar Project Service (Task 4)
2. Implementar Work Item Service (Task 5)
3. Implementar AI Orchestrator (Task 8)
4. E assim por diante...

## Comandos Úteis

```bash
# Ver todos os comandos disponíveis
make help

# Formatar código
make format

# Lint
make lint

# Testes unitários
make test

# Parar serviços
make down

# Limpar tudo (volumes também)
make clean
```
