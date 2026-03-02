# 📚 Índice de Documentação - Bsmart-ALM

## 🚀 Início Rápido

### Para Começar Agora
1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Guia de início rápido (5 minutos)
2. **[RUN_APP.sh](RUN_APP.sh)** - Script para iniciar tudo automaticamente

### Credenciais de Teste
```
Email: admin@test.com
Senha: admin123456
```

### URLs
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8086
- **Swagger**: http://localhost:8086/docs

---

## 📖 Documentação Principal

### Visão Geral
- **[README.md](README.md)** - Visão geral do projeto
- **[MVP_STATUS.md](MVP_STATUS.md)** - Status de implementação do MVP
- **[COMPLETION_REPORT.md](COMPLETION_REPORT.md)** - Relatório de conclusão do frontend

### Guias de Início
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Guia completo de início
- **[QUICK_START.md](QUICK_START.md)** - Quick start guide
- **[START_HERE.md](START_HERE.md)** - Ponto de partida

### Guias de Teste
- **[FRONTEND_TEST_GUIDE.md](FRONTEND_TEST_GUIDE.md)** - Guia de testes do frontend
- **[TEST_GUIDE.md](TEST_GUIDE.md)** - Guia de testes da API
- **[QUICKSTART.md](QUICKSTART.md)** - Quickstart para testes

---

## 🎨 Frontend

### Documentação
- **[frontend/SETUP.md](frontend/SETUP.md)** - Setup completo do frontend
- **[frontend/README.md](frontend/README.md)** - README do frontend
- **[frontend/FRONTEND_GUIDE.md](frontend/FRONTEND_GUIDE.md)** - Guia de implementação

### Estrutura
```
frontend/
├── src/
│   ├── api/          # API client
│   ├── components/   # Componentes (Layout, Sidebar, Header)
│   ├── pages/        # Páginas (Login, Dashboard, Projects, WorkItems)
│   ├── stores/       # State management (Zustand)
│   └── types/        # TypeScript types
├── SETUP.md          # Guia de setup
└── package.json      # Dependências
```

### Páginas Implementadas
1. **Login** - Autenticação JWT
2. **Dashboard** - Estatísticas e resumos
3. **Projects** - CRUD de projetos
4. **WorkItems** - CRUD de work items
5. **ProjectDetail** - Detalhes do projeto (placeholder)
6. **WorkItemDetail** - Detalhes do work item (placeholder)

---

## 🔧 Backend

### Documentação
- **[services/README.md](services/)** - Estrutura dos serviços
- **[TEST_GUIDE.md](TEST_GUIDE.md)** - Guia de testes da API

### Serviços Implementados
1. **Identity Service** - Autenticação e autorização
2. **Project Service** - Gerenciamento de projetos
3. **Work Item Service** - Gerenciamento de work items
4. **API Gateway** - Gateway principal

### Estrutura
```
services/
├── api_gateway/      # API Gateway
├── identity/         # Auth & Users
├── project/          # Projects
├── work_item/        # Work Items
└── shared/           # Código compartilhado
```

---

## 📋 Especificações

### Spec do Projeto
- **[.kiro/specs/bsmart-alm-platform/requirements.md](.kiro/specs/bsmart-alm-platform/requirements.md)** - Requisitos
- **[.kiro/specs/bsmart-alm-platform/design.md](.kiro/specs/bsmart-alm-platform/design.md)** - Design
- **[.kiro/specs/bsmart-alm-platform/tasks.md](.kiro/specs/bsmart-alm-platform/tasks.md)** - Tasks

### Status das Tasks
- ✅ Tasks 1-5: Completas (Infra, Identity, Project, Work Item)
- 🔄 Task 6+: Pendentes (Artifact, Event Bus, AI, etc)

---

## 🛠️ Scripts e Ferramentas

### Scripts de Automação
- **[RUN_APP.sh](RUN_APP.sh)** - Iniciar backend + frontend automaticamente
- **[STOP_APP.sh](STOP_APP.sh)** - Parar todos os serviços
- **[scripts/seed_db.py](scripts/seed_db.py)** - Popular banco de dados
- **[scripts/test_api.py](scripts/test_api.py)** - Testar API

### Makefile
```bash
make dev        # Iniciar backend
make seed       # Popular banco
make test-api   # Testar API
make clean      # Limpar cache
```

### Docker
```bash
docker-compose up -d      # Iniciar containers
docker-compose down       # Parar containers
docker-compose ps         # Ver status
docker-compose logs -f    # Ver logs
```

---

## 🗄️ Banco de Dados

### Migrações
- **[alembic/](alembic/)** - Diretório de migrações
- **[alembic.ini](alembic.ini)** - Configuração do Alembic

### Comandos
```bash
# Criar migração
uv run alembic revision --autogenerate -m "description"

# Aplicar migração
uv run alembic upgrade head

# Reverter migração
uv run alembic downgrade -1
```

---

## 🧪 Testes

### Guias de Teste
1. **[FRONTEND_TEST_GUIDE.md](FRONTEND_TEST_GUIDE.md)** - Testes do frontend
2. **[TEST_GUIDE.md](TEST_GUIDE.md)** - Testes da API
3. **[tests/](tests/)** - Diretório de testes

### Executar Testes
```bash
# Testes da API
make test-api

# Testes unitários (quando implementados)
pytest

# Testes E2E (quando implementados)
npm run test:e2e
```

---

## 📦 Configuração

### Arquivos de Configuração
- **[.env](.env)** - Variáveis de ambiente
- **[.env.example](.env.example)** - Exemplo de variáveis
- **[docker-compose.yml](docker-compose.yml)** - Configuração Docker
- **[pyproject.toml](pyproject.toml)** - Dependências Python
- **[frontend/package.json](frontend/package.json)** - Dependências Node

### Portas Utilizadas
- **8086** - API Backend
- **3000** - Frontend
- **5437** - PostgreSQL
- **5677** - RabbitMQ AMQP
- **15677** - RabbitMQ Management
- **9000** - MinIO API
- **9001** - MinIO Console
- **6379** - Redis

---

## 🎯 Próximos Passos

### Implementação Sugerida
1. **Task 6** - Artifact & Evidence Service
2. **Task 7** - Event Bus Infrastructure
3. **Task 8** - AI Orchestrator Service
4. **Task 9** - RAG Service
5. **Task 10** - Prompt Registry Service

### Melhorias do Frontend
1. Implementar páginas de detalhes completas
2. Adicionar edição de projetos e work items
3. Implementar transições de estado
4. Adicionar testes E2E

---

## 📊 Estatísticas do Projeto

### Backend
- **Serviços**: 4
- **Endpoints**: 35+
- **Modelos**: 13
- **Linhas de código**: ~5,000+

### Frontend
- **Páginas**: 4 completas + 2 placeholders
- **Componentes**: 3
- **Linhas de código**: ~460
- **Tecnologias**: React 18, TypeScript, Tailwind CSS

### Documentação
- **Arquivos**: 15+
- **Linhas**: ~2,000+
- **Guias**: 8

---

## 🆘 Suporte

### Problemas Comuns
Veja a seção "Problemas Comuns" em:
- [GETTING_STARTED.md](GETTING_STARTED.md#-problemas-comuns)
- [FRONTEND_TEST_GUIDE.md](FRONTEND_TEST_GUIDE.md#-problemas-comuns)

### Logs
```bash
# Backend
tail -f logs/backend.log

# Frontend
tail -f logs/frontend.log

# Docker
docker-compose logs -f
```

---

## 📞 Contato

Para dúvidas ou sugestões, consulte a documentação ou abra uma issue no repositório.

---

## 🎉 Status do Projeto

**MVP Status**: ✅ **COMPLETO**

- ✅ Backend funcional (Tasks 1-5)
- ✅ Frontend funcional (100%)
- ✅ Documentação completa
- ✅ Scripts de automação
- ✅ Pronto para uso e expansão

**Última atualização**: 23 de Fevereiro de 2026

---

**Bsmart-ALM - AI-First Application Lifecycle Management Platform** 🚀
