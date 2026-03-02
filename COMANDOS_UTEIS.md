# 🔧 Comandos Úteis - Bsmart-ALM

## 🚀 Início Rápido

### Iniciar Sistema Completo
```bash
./START_COMPLETE_SYSTEM.sh
```

### Iniciar Apenas Backend
```bash
./RUN_APP.sh
```

### Iniciar Apenas Frontend (Dev)
```bash
./START_FRONTEND_DEV.sh
```

---

## 🗄️ Banco de Dados

### Iniciar PostgreSQL
```bash
docker-compose up -d postgres
```

### Parar PostgreSQL
```bash
docker-compose stop postgres
```

### Ver Logs do PostgreSQL
```bash
docker-compose logs -f postgres
```

### Executar Migração de AI Stats
```bash
uv run python scripts/migrate_ai_stats.py
```

### Seed do Banco
```bash
uv run python scripts/seed_db.py
```

### Reset Completo do Banco
```bash
uv run python scripts/reset_and_seed.py
```

### Conectar ao PostgreSQL
```bash
docker exec -it bsmart-alm-postgres-1 psql -U postgres -d bsmart_alm
```

### Backup do Banco
```bash
docker exec bsmart-alm-postgres-1 pg_dump -U postgres bsmart_alm > backup.sql
```

### Restaurar Backup
```bash
cat backup.sql | docker exec -i bsmart-alm-postgres-1 psql -U postgres bsmart_alm
```

---

## 🐍 Backend

### Instalar Dependências
```bash
uv sync
```

### Iniciar Servidor de Desenvolvimento
```bash
uv run uvicorn services.api_gateway.main:app --reload
```

### Iniciar em Porta Específica
```bash
uv run uvicorn services.api_gateway.main:app --reload --port 8080
```

### Ver Logs do Backend
```bash
# Logs aparecem no terminal onde o servidor foi iniciado
```

### Executar Script Python
```bash
uv run python scripts/nome_do_script.py
```

### Executar Testes
```bash
uv run pytest
```

### Executar Testes com Cobertura
```bash
uv run pytest --cov=services --cov-report=html
```

---

## ⚛️ Frontend

### Instalar Dependências
```bash
cd frontend
npm install
```

### Iniciar Servidor de Desenvolvimento
```bash
cd frontend
npm run dev
```

### Build para Produção
```bash
cd frontend
npm run build
```

### Preview do Build
```bash
cd frontend
npm run preview
```

### Limpar Cache e Reinstalar
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Verificar Erros TypeScript
```bash
cd frontend
npm run build
```

---

## 🐳 Docker

### Iniciar Todos os Serviços
```bash
docker-compose up -d
```

### Parar Todos os Serviços
```bash
docker-compose down
```

### Ver Status dos Serviços
```bash
docker-compose ps
```

### Ver Logs de Todos os Serviços
```bash
docker-compose logs -f
```

### Ver Logs de um Serviço Específico
```bash
docker-compose logs -f postgres
docker-compose logs -f ollama
```

### Reiniciar um Serviço
```bash
docker-compose restart postgres
```

### Remover Volumes (CUIDADO!)
```bash
docker-compose down -v
```

### Rebuild de Imagens
```bash
docker-compose build
docker-compose up -d
```

---

## 🤖 Ollama (IA)

### Verificar se Ollama está Rodando
```bash
curl http://localhost:11434/api/tags
```

### Listar Modelos Instalados
```bash
docker exec -it bsmart-ollama ollama list
```

### Baixar Modelo
```bash
docker exec -it bsmart-ollama ollama pull llama3.2
```

### Remover Modelo
```bash
docker exec -it bsmart-ollama ollama rm llama3.2
```

### Testar Modelo
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Hello, world!",
  "stream": false
}'
```

---

## 🔍 Debugging

### Ver Logs do Backend em Tempo Real
```bash
# Terminal onde o backend está rodando
# Ou se estiver em Docker:
docker-compose logs -f api
```

### Ver Logs do Frontend
```bash
# Console do navegador (F12)
# Ou terminal onde npm run dev está rodando
```

### Verificar Conexão com Banco
```bash
docker exec -it bsmart-alm-postgres-1 psql -U postgres -d bsmart_alm -c "SELECT COUNT(*) FROM tenant;"
```

### Verificar Tabelas do Banco
```bash
docker exec -it bsmart-alm-postgres-1 psql -U postgres -d bsmart_alm -c "\dt"
```

### Ver Estrutura de uma Tabela
```bash
docker exec -it bsmart-alm-postgres-1 psql -U postgres -d bsmart_alm -c "\d ai_usage_stats"
```

### Verificar Dados de AI Stats
```bash
docker exec -it bsmart-alm-postgres-1 psql -U postgres -d bsmart_alm -c "SELECT * FROM ai_usage_stats LIMIT 5;"
```

---

## 🧹 Limpeza

### Limpar Cache do Frontend
```bash
cd frontend
rm -rf node_modules package-lock.json dist
npm install
```

### Limpar Cache do Python
```bash
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### Limpar Docker
```bash
docker system prune -a
```

### Limpar Volumes Docker (CUIDADO!)
```bash
docker volume prune
```

---

## 📊 Monitoramento

### Ver Uso de Recursos Docker
```bash
docker stats
```

### Ver Espaço em Disco
```bash
df -h
```

### Ver Processos Python
```bash
ps aux | grep python
```

### Ver Processos Node
```bash
ps aux | grep node
```

### Matar Processo na Porta 8000
```bash
lsof -ti:8000 | xargs kill -9
```

### Matar Processo na Porta 5173
```bash
lsof -ti:5173 | xargs kill -9
```

---

## 🔐 Segurança

### Gerar Nova Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Ver Variáveis de Ambiente
```bash
cat .env
```

### Editar Variáveis de Ambiente
```bash
nano .env
# ou
vim .env
```

---

## 📦 Dependências

### Atualizar Dependências Python
```bash
uv sync --upgrade
```

### Atualizar Dependências Frontend
```bash
cd frontend
npm update
```

### Ver Dependências Desatualizadas (Frontend)
```bash
cd frontend
npm outdated
```

### Adicionar Nova Dependência Python
```bash
uv add nome-do-pacote
```

### Adicionar Nova Dependência Frontend
```bash
cd frontend
npm install nome-do-pacote
```

---

## 🧪 Testes

### Testar API com curl
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Listar Projetos (substitua TOKEN)
curl http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer TOKEN"
```

### Testar Endpoint de AI Stats
```bash
curl http://localhost:8000/api/v1/ai-stats \
  -H "Authorization: Bearer TOKEN"
```

### Testar Frontend
```bash
# Abrir no navegador
open http://localhost:5173
# ou
xdg-open http://localhost:5173
```

---

## 📝 Git

### Ver Status
```bash
git status
```

### Adicionar Arquivos
```bash
git add .
```

### Commit
```bash
git commit -m "Mensagem do commit"
```

### Push
```bash
git push origin main
```

### Ver Histórico
```bash
git log --oneline
```

### Ver Diferenças
```bash
git diff
```

---

## 🎯 Atalhos Úteis

### Reiniciar Tudo
```bash
docker-compose restart
./RUN_APP.sh &
cd frontend && npm run dev
```

### Verificar Saúde do Sistema
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:5173

# PostgreSQL
docker exec -it bsmart-alm-postgres-1 pg_isready

# Ollama
curl http://localhost:11434/api/tags
```

### Backup Rápido
```bash
# Banco
docker exec bsmart-alm-postgres-1 pg_dump -U postgres bsmart_alm > backup_$(date +%Y%m%d).sql

# Código
tar -czf backup_code_$(date +%Y%m%d).tar.gz --exclude=node_modules --exclude=__pycache__ --exclude=.git .
```

---

## 🆘 Emergência

### Sistema Não Inicia
```bash
# 1. Parar tudo
docker-compose down
pkill -f uvicorn
pkill -f node

# 2. Limpar
docker system prune -f
cd frontend && rm -rf node_modules && npm install

# 3. Reiniciar
./START_COMPLETE_SYSTEM.sh
```

### Banco Corrompido
```bash
# 1. Backup (se possível)
docker exec bsmart-alm-postgres-1 pg_dump -U postgres bsmart_alm > emergency_backup.sql

# 2. Reset
docker-compose down -v
docker-compose up -d postgres
sleep 5

# 3. Restaurar ou Seed
uv run python scripts/reset_and_seed.py
```

### Frontend Não Compila
```bash
cd frontend
rm -rf node_modules package-lock.json dist .vite
npm cache clean --force
npm install
npm run build
```

---

## 📚 Documentação

### Ver Documentação da API
```bash
# Abrir no navegador
open http://localhost:8000/docs
```

### Gerar Documentação
```bash
# Backend (Swagger)
# Já disponível em /docs

# Frontend (TypeDoc)
cd frontend
npm install --save-dev typedoc
npx typedoc --out docs src
```

---

## 🎉 Comandos Mais Usados

```bash
# Iniciar sistema
./START_COMPLETE_SYSTEM.sh

# Ver logs
docker-compose logs -f

# Reiniciar backend
pkill -f uvicorn && ./RUN_APP.sh

# Rebuild frontend
cd frontend && npm run build

# Migração
uv run python scripts/migrate_ai_stats.py

# Seed
uv run python scripts/seed_db.py

# Verificar saúde
curl http://localhost:8000/health
```

---

## 💡 Dicas

1. **Use aliases** no seu `.bashrc` ou `.zshrc`:
```bash
alias bsmart-start='./START_COMPLETE_SYSTEM.sh'
alias bsmart-logs='docker-compose logs -f'
alias bsmart-restart='docker-compose restart && ./RUN_APP.sh'
```

2. **Mantenha múltiplos terminais abertos**:
   - Terminal 1: Backend
   - Terminal 2: Frontend
   - Terminal 3: Comandos gerais

3. **Use tmux ou screen** para sessões persistentes

4. **Configure seu editor** para auto-reload

5. **Use o console do navegador** (F12) para debug do frontend

---

**Última atualização**: 2024  
**Versão**: 1.0.0
