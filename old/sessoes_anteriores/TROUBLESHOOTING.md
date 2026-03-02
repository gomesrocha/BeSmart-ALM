# 🔧 Troubleshooting - Bsmart-ALM

## Problemas Comuns e Soluções

### 1. docker-compose: comando não encontrado

**Problema**: Você tem Docker Compose V2 instalado.

**Solução**: Use `docker compose` (sem hífen) ao invés de `docker-compose`:

```bash
# Ao invés de:
docker-compose up -d

# Use:
docker compose up -d
```

Os scripts já foram atualizados para usar o comando correto.

---

### 2. Porta 8086 já em uso

**Problema**: O backend já está rodando ou outro processo está usando a porta.

**Solução 1 - Matar o processo**:
```bash
# Encontrar o processo
lsof -i :8086

# Matar o processo
kill -9 <PID>
```

**Solução 2 - Usar o script atualizado**:
```bash
./RUN_APP.sh
# O script agora mata automaticamente o processo na porta 8086
```

**Solução 3 - Mudar a porta**:
```bash
# Editar .env
API_PORT=8087

# Ou rodar manualmente
uv run uvicorn services.api_gateway.main:app --reload --port 8087
```

---

### 3. Frontend não conecta ao backend

**Problema**: Proxy do Vite não está configurado corretamente.

**Solução**: Verificar `frontend/vite.config.ts`:

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8086',  // Verificar porta
        changeOrigin: true,
      },
    },
  },
})
```

---

### 4. Banco de dados vazio

**Problema**: Tabelas não foram criadas ou dados não foram populados.

**Solução**:
```bash
# Aplicar migrações
uv run alembic upgrade head

# Popular dados
make seed
# Ou: uv run python scripts/seed_db.py
```

---

### 5. Docker não inicia

**Problema**: Containers não sobem ou ficam em estado de erro.

**Solução 1 - Resetar tudo**:
```bash
# Parar e remover tudo
docker compose down -v

# Iniciar novamente
docker compose up -d

# Aguardar
sleep 10

# Verificar status
docker compose ps
```

**Solução 2 - Ver logs**:
```bash
# Ver logs de todos os containers
docker compose logs -f

# Ver logs de um container específico
docker compose logs -f postgres
docker compose logs -f rabbitmq
```

---

### 6. Erro de migração do Alembic

**Problema**: Erro ao aplicar migrações.

**Solução 1 - Resetar banco**:
```bash
# Parar e remover volumes
docker compose down -v

# Iniciar novamente
docker compose up -d
sleep 10

# Aplicar migrações
uv run alembic upgrade head

# Popular dados
make seed
```

**Solução 2 - Criar nova migração**:
```bash
# Criar nova migração
uv run alembic revision --autogenerate -m "fix schema"

# Aplicar
uv run alembic upgrade head
```

---

### 7. Frontend - npm install falha

**Problema**: Erro ao instalar dependências do frontend.

**Solução**:
```bash
cd frontend

# Limpar cache
rm -rf node_modules package-lock.json

# Reinstalar
npm install

# Se ainda falhar, usar npm ci
npm ci
```

---

### 8. Backend não inicia

**Problema**: Erro ao iniciar o uvicorn.

**Solução 1 - Verificar dependências**:
```bash
# Reinstalar dependências
uv sync

# Verificar se UV está atualizado
uv --version
```

**Solução 2 - Verificar logs**:
```bash
# Ver logs detalhados
uv run uvicorn services.api_gateway.main:app --reload --port 8086 --log-level debug
```

**Solução 3 - Verificar banco**:
```bash
# Testar conexão com banco
docker compose ps postgres

# Ver logs do postgres
docker compose logs postgres
```

---

### 9. Erro 401 no frontend

**Problema**: Token JWT expirado ou inválido.

**Solução**:
```bash
# No navegador:
1. Abrir DevTools (F12)
2. Application > Local Storage
3. Deletar 'token'
4. Fazer login novamente
```

---

### 10. Containers não param

**Problema**: `docker compose down` não funciona.

**Solução**:
```bash
# Forçar parada
docker compose down --remove-orphans

# Se ainda não funcionar
docker compose kill
docker compose rm -f

# Limpar tudo
docker system prune -a --volumes
```

---

## 🔍 Comandos de Diagnóstico

### Verificar Status Geral
```bash
# Docker
docker compose ps

# Backend
curl http://localhost:8086/health

# Frontend
curl http://localhost:3000

# Banco de dados
docker compose exec postgres psql -U postgres -d bsmart_alm -c "\dt"
```

### Ver Logs
```bash
# Backend
tail -f logs/backend.log

# Frontend
tail -f logs/frontend.log

# Docker
docker compose logs -f
docker compose logs -f postgres
docker compose logs -f rabbitmq
```

### Verificar Portas
```bash
# Ver todas as portas em uso
lsof -i -P -n | grep LISTEN

# Verificar porta específica
lsof -i :8086
lsof -i :3000
lsof -i :5437
```

### Verificar Processos
```bash
# Ver processos Python
ps aux | grep python

# Ver processos Node
ps aux | grep node

# Ver processos do projeto
ps aux | grep -E "(uvicorn|vite)"
```

---

## 🆘 Resetar Tudo (Última Opção)

Se nada funcionar, resetar completamente:

```bash
# 1. Parar tudo
./STOP_APP.sh

# 2. Matar processos manualmente
pkill -f uvicorn
pkill -f vite

# 3. Limpar Docker
docker compose down -v
docker system prune -a --volumes -f

# 4. Limpar cache Python
rm -rf .venv __pycache__ **/__pycache__

# 5. Limpar frontend
rm -rf frontend/node_modules frontend/.vite

# 6. Reiniciar do zero
docker compose up -d
sleep 15
uv sync
uv run alembic upgrade head
make seed
cd frontend && npm install && cd ..

# 7. Iniciar
./RUN_APP.sh
```

---

## 📞 Ainda com Problemas?

### Verificar Pré-requisitos
```bash
# Docker
docker --version
docker compose version

# UV
uv --version

# Node
node --version
npm --version

# Python
python --version
```

### Verificar Configuração
```bash
# Variáveis de ambiente
cat .env

# Docker Compose
cat docker-compose.yml

# Vite config
cat frontend/vite.config.ts
```

### Coletar Informações
```bash
# Sistema
uname -a

# Portas em uso
netstat -tuln | grep -E "(8086|3000|5437)"

# Espaço em disco
df -h

# Memória
free -h
```

---

## 💡 Dicas de Prevenção

### 1. Sempre verificar status antes de iniciar
```bash
docker compose ps
lsof -i :8086
lsof -i :3000
```

### 2. Usar os scripts fornecidos
```bash
./RUN_APP.sh    # Inicia com verificações
./STOP_APP.sh   # Para corretamente
```

### 3. Manter logs limpos
```bash
# Limpar logs antigos
rm -rf logs/*.log
```

### 4. Atualizar dependências regularmente
```bash
# Backend
uv sync

# Frontend
cd frontend && npm update && cd ..
```

### 5. Fazer backup do banco antes de mudanças
```bash
# Backup
docker compose exec postgres pg_dump -U postgres bsmart_alm > backup.sql

# Restore
docker compose exec -T postgres psql -U postgres bsmart_alm < backup.sql
```

---

## 📚 Documentação Relacionada

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Guia de início
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Referência rápida
- **[INDEX.md](INDEX.md)** - Índice completo

---

**Problemas resolvidos!** ✅
