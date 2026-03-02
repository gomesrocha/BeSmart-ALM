# ⚡ Quick Reference - Bsmart-ALM

## 🚀 Início Rápido (30 segundos)

```bash
./RUN_APP.sh
```

Abra: **http://localhost:3000**

Login: **admin@test.com** / **admin123456**

---

## 📋 Comandos Essenciais

### Iniciar/Parar
```bash
./RUN_APP.sh          # Iniciar tudo
./STOP_APP.sh         # Parar tudo
```

### Backend
```bash
make dev              # Iniciar backend
make seed             # Popular banco
make test-api         # Testar API
```

### Frontend
```bash
cd frontend
npm install           # Instalar dependências
npm run dev           # Iniciar dev server
npm run build         # Build produção
```

### Docker
```bash
docker-compose up -d      # Iniciar containers
docker-compose down       # Parar containers
docker-compose ps         # Ver status
docker-compose logs -f    # Ver logs
```

### Banco de Dados
```bash
uv run alembic upgrade head              # Aplicar migrações
uv run alembic revision --autogenerate   # Criar migração
make seed                                # Popular dados
```

---

## 🌐 URLs

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Frontend** | http://localhost:3000 | Interface web |
| **Backend** | http://localhost:8086 | API REST |
| **Swagger** | http://localhost:8086/docs | Documentação API |
| **ReDoc** | http://localhost:8086/redoc | Documentação alternativa |
| **RabbitMQ** | http://localhost:15677 | Management UI |
| **MinIO** | http://localhost:9001 | Console |

---

## 🔐 Credenciais

### Aplicação
```
Email: admin@test.com
Senha: admin123456
```

### RabbitMQ
```
User: guest
Pass: guest
```

### MinIO
```
User: minioadmin
Pass: minioadmin
```

---

## 📁 Estrutura de Pastas

```
bsmart-alm-platform/
├── frontend/           # React frontend
│   └── src/
│       ├── pages/     # Páginas
│       ├── components/ # Componentes
│       ├── api/       # API client
│       └── stores/    # State management
├── services/          # Backend services
│   ├── api_gateway/  # Gateway
│   ├── identity/     # Auth
│   ├── project/      # Projects
│   └── work_item/    # Work Items
├── scripts/          # Scripts úteis
├── tests/            # Testes
└── alembic/          # Migrações DB
```

---

## 🎯 Funcionalidades

### Frontend
- ✅ Login/Logout
- ✅ Dashboard
- ✅ Projetos (CRUD)
- ✅ Work Items (CRUD)
- ✅ Filtros e busca
- ✅ Design responsivo

### Backend
- ✅ Autenticação JWT
- ✅ RBAC (6 roles)
- ✅ Multi-tenancy
- ✅ API REST (35+ endpoints)
- ✅ State machine
- ✅ Rastreabilidade

---

## 📚 Documentação

| Arquivo | Descrição |
|---------|-----------|
| **INDEX.md** | Índice completo |
| **GETTING_STARTED.md** | Guia de início |
| **FRONTEND_TEST_GUIDE.md** | Testes frontend |
| **TEST_GUIDE.md** | Testes API |
| **MVP_STATUS.md** | Status do MVP |
| **COMPLETION_REPORT.md** | Relatório final |

---

## 🐛 Troubleshooting

### Backend não inicia
```bash
# Verificar se porta está livre
lsof -i :8086

# Verificar logs
tail -f logs/backend.log
```

### Frontend não conecta
```bash
# Verificar se backend está rodando
curl http://localhost:8086/health

# Verificar proxy no vite.config.ts
```

### Banco de dados vazio
```bash
# Popular novamente
make seed
```

### Docker não inicia
```bash
# Resetar tudo
docker-compose down -v
docker-compose up -d
sleep 10
uv run alembic upgrade head
make seed
```

---

## 🔧 Portas Utilizadas

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Frontend | 3000 | Vite dev server |
| Backend | 8086 | FastAPI |
| PostgreSQL | 5437 | Database |
| RabbitMQ AMQP | 5677 | Message broker |
| RabbitMQ Mgmt | 15677 | Web UI |
| MinIO API | 9000 | Object storage |
| MinIO Console | 9001 | Web UI |
| Redis | 6379 | Cache |

---

## 📊 Status do Projeto

### Implementado (✅)
- Infraestrutura
- Identity Service
- Project Service
- Work Item Service
- Frontend completo
- Documentação

### Pendente (🔄)
- Artifact Service
- Event Bus
- AI Orchestrator
- RAG Service
- Requirements Module
- Analysis Module

---

## 🎨 Design System

### Cores
```css
Primary:  #0ea5e9  (Blue)
Success:  #10b981  (Green)
Warning:  #f59e0b  (Yellow)
Danger:   #ef4444  (Red)
```

### Classes CSS
```css
.btn              /* Button base */
.btn-primary      /* Primary button */
.btn-secondary    /* Secondary button */
.card             /* Card container */
.input            /* Input field */
```

---

## 🧪 Testes Rápidos

### Testar Backend
```bash
# Health check
curl http://localhost:8086/health

# Login
curl -X POST http://localhost:8086/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123456"}'
```

### Testar Frontend
1. Abrir http://localhost:3000
2. Fazer login
3. Criar um projeto
4. Criar um work item
5. Testar filtros

---

## 💡 Dicas Úteis

### Ver Logs
```bash
# Backend
tail -f logs/backend.log

# Frontend
tail -f logs/frontend.log

# Docker
docker-compose logs -f postgres
docker-compose logs -f rabbitmq
```

### Limpar Tudo
```bash
# Parar serviços
./STOP_APP.sh

# Limpar Docker
docker-compose down -v

# Limpar cache Python
make clean

# Limpar node_modules
rm -rf frontend/node_modules
```

### Reiniciar do Zero
```bash
# 1. Limpar tudo
docker-compose down -v
rm -rf frontend/node_modules

# 2. Iniciar Docker
docker-compose up -d
sleep 10

# 3. Configurar banco
uv run alembic upgrade head
make seed

# 4. Instalar frontend
cd frontend && npm install && cd ..

# 5. Iniciar tudo
./RUN_APP.sh
```

---

## 🎯 Próximos Passos

### Hoje
1. Testar todas as funcionalidades
2. Validar responsividade
3. Verificar documentação

### Esta Semana
1. Implementar páginas de detalhes
2. Adicionar edição
3. Implementar transições de estado

### Este Mês
1. Adicionar novos módulos
2. Implementar testes E2E
3. Adicionar funcionalidades avançadas

---

## 📞 Ajuda

### Documentação Completa
```bash
cat INDEX.md              # Índice
cat GETTING_STARTED.md    # Início
cat FRONTEND_TEST_GUIDE.md # Testes
```

### Swagger UI
http://localhost:8086/docs

### Logs
```bash
ls -la logs/
```

---

## ✅ Checklist Rápido

Antes de começar:
- [ ] Docker instalado e rodando
- [ ] UV instalado
- [ ] Node.js instalado
- [ ] Portas livres (3000, 8086, 5437, etc)

Para iniciar:
- [ ] `./RUN_APP.sh`
- [ ] Abrir http://localhost:3000
- [ ] Fazer login
- [ ] Testar funcionalidades

---

**Bsmart-ALM - Pronto para uso!** 🚀

*Última atualização: 23 de Fevereiro de 2026*
