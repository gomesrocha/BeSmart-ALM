# 🚀 Getting Started - Bsmart-ALM

## Início Rápido (5 minutos)

### 1️⃣ Pré-requisitos

```bash
# Verificar instalações
docker --version
uv --version
node --version
npm --version
```

Se não tiver instalado:
- **Docker**: https://docs.docker.com/get-docker/
- **UV**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Node.js**: https://nodejs.org/ (v18+)

### 2️⃣ Clonar e Configurar

```bash
# Clonar o repositório (se ainda não fez)
git clone <repo-url>
cd bsmart-alm-platform

# Copiar variáveis de ambiente
cp .env.example .env
```

### 3️⃣ Iniciar Infraestrutura

```bash
# Subir Docker (PostgreSQL, RabbitMQ, MinIO, Redis)
docker-compose up -d

# Verificar se está rodando
docker-compose ps
```

Você deve ver:
- ✅ postgres (porta 5437)
- ✅ rabbitmq (portas 5677, 15677)
- ✅ minio (portas 9000, 9001)
- ✅ redis (porta 6379)

### 4️⃣ Configurar Banco de Dados

```bash
# Criar migração inicial
uv run alembic revision --autogenerate -m "initial schema"

# Aplicar migração
uv run alembic upgrade head

# Popular com dados de teste
make seed
```

Isso cria:
- 1 tenant: "Test Organization"
- 6 roles padrão
- 3 usuários de teste

### 5️⃣ Iniciar Backend

```bash
# Terminal 1
make dev

# Ou manualmente:
# uv run uvicorn services.api_gateway.main:app --reload --port 8086
```

Aguarde até ver:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8086
```

### 6️⃣ Iniciar Frontend

```bash
# Terminal 2
cd frontend
npm install
npm run dev
```

Aguarde até ver:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

### 7️⃣ Acessar a Aplicação

Abra seu navegador em: **http://localhost:3000**

**Credenciais de teste:**
```
Email: admin@test.com
Senha: admin123456
```

## ✅ Verificação Rápida

### Backend está funcionando?

```bash
# Testar health check
curl http://localhost:8086/health

# Deve retornar: {"status":"healthy"}
```

### Frontend está funcionando?

Abra http://localhost:3000 - deve ver a tela de login.

### Banco de dados está populado?

```bash
# Testar login via API
curl -X POST http://localhost:8086/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123456"}'

# Deve retornar um token JWT
```

## 🎯 Próximos Passos

### 1. Explorar o Frontend

- ✅ Fazer login
- ✅ Ver o Dashboard
- ✅ Criar um projeto
- ✅ Criar work items
- ✅ Testar filtros e busca

### 2. Explorar a API

Acesse a documentação interativa:
- **Swagger UI**: http://localhost:8086/docs
- **ReDoc**: http://localhost:8086/redoc

### 3. Testar Funcionalidades

Siga o guia: `FRONTEND_TEST_GUIDE.md`

### 4. Desenvolver Novas Features

Veja as próximas tasks em: `.kiro/specs/bsmart-alm-platform/tasks.md`

## 🐛 Problemas Comuns

### Porta já em uso

Se a porta 8086 já estiver em uso:

```bash
# Encontrar processo
lsof -i :8086

# Matar processo
kill -9 <PID>
```

Ou edite `.env` e mude `API_PORT=8086` para outra porta.

### Docker não inicia

```bash
# Parar tudo
docker-compose down

# Limpar volumes
docker-compose down -v

# Iniciar novamente
docker-compose up -d
```

### Erro de migração

```bash
# Resetar banco
docker-compose down -v
docker-compose up -d

# Aguardar 10 segundos
sleep 10

# Aplicar migração novamente
uv run alembic upgrade head
make seed
```

### Frontend não conecta ao backend

Verifique o `frontend/vite.config.ts`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8086',
    changeOrigin: true,
  },
}
```

## 📚 Documentação

- **README.md** - Visão geral do projeto
- **MVP_STATUS.md** - Status de implementação
- **FRONTEND_TEST_GUIDE.md** - Guia de testes do frontend
- **TEST_GUIDE.md** - Guia de testes da API
- **frontend/SETUP.md** - Setup detalhado do frontend

## 🎉 Pronto!

Você agora tem:
- ✅ Backend rodando em http://localhost:8086
- ✅ Frontend rodando em http://localhost:3000
- ✅ Banco de dados populado
- ✅ Usuários de teste criados

**Comece a explorar o Bsmart-ALM!** 🚀

## 💡 Dicas

### Comandos Úteis

```bash
# Ver logs do backend
make dev

# Ver logs do Docker
docker-compose logs -f

# Parar tudo
docker-compose down
# Ctrl+C nos terminais do backend e frontend

# Reiniciar tudo
docker-compose restart
```

### Atalhos do Makefile

```bash
make dev        # Iniciar backend
make seed       # Popular banco
make test-api   # Testar API
make clean      # Limpar cache
```

### Estrutura de Pastas

```
bsmart-alm-platform/
├── services/           # Backend services
│   ├── api_gateway/   # API Gateway
│   ├── identity/      # Auth & Users
│   ├── project/       # Projects
│   ├── work_item/     # Work Items
│   └── shared/        # Shared code
├── frontend/          # React frontend
│   ├── src/
│   │   ├── pages/    # Pages
│   │   ├── components/ # Components
│   │   ├── api/      # API client
│   │   └── stores/   # State management
├── alembic/          # DB migrations
├── scripts/          # Utility scripts
└── tests/            # Tests
```

**Divirta-se desenvolvendo!** 🎊
