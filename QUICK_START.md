# Quick Start - Bsmart-ALM (Sem Alembic)

## Passo 1: Subir Docker

```bash
docker-compose up -d
```

Aguarde os serviços iniciarem (PostgreSQL:5437, RabbitMQ:5677, MinIO, Redis).

## Passo 2: Instalar Dependências

```bash
uv sync
```

## Passo 3: Popular Banco (cria tabelas automaticamente)

```bash
uv run python scripts/seed_db.py
```

Este script:
- Cria todas as tabelas automaticamente via SQLModel
- Popula com dados de teste:
  - 1 tenant: "Test Organization"
  - 6 roles padrão (admin, po, dev, qa, sec, auditor)
  - 3 usuários:
    - admin@test.com / admin123456
    - dev@test.com / dev123456
    - po@test.com / po123456

## Passo 4: Rodar Servidor

```bash
uv run uvicorn services.api_gateway.main:app --reload --port 8086
```

Ou use o Makefile:
```bash
make dev
```

## Passo 5: Testar

### Opção A: Swagger UI
Abra: http://localhost:8086/docs

### Opção B: Script Automatizado
```bash
uv run python scripts/test_api.py
```

### Opção C: cURL
```bash
# Login
curl -X POST http://localhost:8086/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123456"}'

# Copie o access_token e use nos próximos comandos

# Ver usuário atual
curl -X GET http://localhost:8086/api/v1/auth/me \
  -H "Authorization: Bearer SEU_TOKEN"

# Listar projetos
curl -X GET http://localhost:8086/api/v1/projects \
  -H "Authorization: Bearer SEU_TOKEN"
```

## Comandos Úteis

```bash
# Ver logs do Docker
docker-compose logs -f

# Parar serviços
docker-compose down

# Limpar tudo (incluindo volumes)
docker-compose down -v

# Recriar banco do zero
docker-compose down -v
docker-compose up -d
uv run python scripts/seed_db.py
```

## Portas Usadas

- API: 8086
- PostgreSQL: 5437
- RabbitMQ AMQP: 5677
- RabbitMQ Management: 15677 (http://localhost:15677 - guest/guest)
- MinIO API: 9000
- MinIO Console: 9001 (http://localhost:9001 - minioadmin/minioadmin)
- Redis: 6379

## Troubleshooting

### Erro de conexão com PostgreSQL
```bash
# Verificar se está rodando
docker-compose ps postgres

# Ver logs
docker-compose logs postgres

# Reiniciar
docker-compose restart postgres
```

### Recriar banco do zero
```bash
docker-compose down -v
docker-compose up -d
# Aguardar ~10 segundos
uv run python scripts/seed_db.py
```

### Porta em uso
Se a porta 8086 estiver em uso, mude no comando:
```bash
uv run uvicorn services.api_gateway.main:app --reload --port 8087
```

## Pronto! 🎉

Agora você tem:
- ✅ 35 endpoints REST funcionais
- ✅ Autenticação JWT
- ✅ RBAC com 6 roles
- ✅ Gerenciamento de projetos
- ✅ Sistema de work items com state machine
- ✅ Multi-tenancy completo

Acesse a documentação interativa em: http://localhost:8086/docs
