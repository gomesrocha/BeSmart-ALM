# 🚀 START HERE - Bsmart-ALM

## ⚡ Início Mais Rápido (1 comando)

```bash
./RUN_APP.sh
```

Isso vai:
- ✅ Verificar e iniciar Docker
- ✅ Configurar banco de dados
- ✅ Iniciar backend (porta 8086)
- ✅ Iniciar frontend (porta 3000)

## 🌐 Acessar

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8086
- **Swagger**: http://localhost:8086/docs

## 🔐 Credenciais

```
Email: admin@test.com
Senha: admin123456
```

## 📚 Documentação

### Início Rápido
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Guia completo (5 min)
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Referência rápida
- **[INDEX.md](INDEX.md)** - Índice de toda documentação

### Testes
- **[FRONTEND_TEST_GUIDE.md](FRONTEND_TEST_GUIDE.md)** - Testes do frontend
- **[TEST_GUIDE.md](TEST_GUIDE.md)** - Testes da API

### Status
- **[MVP_STATUS.md](MVP_STATUS.md)** - Status de implementação
- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Resumo executivo
- **[WHAT_WAS_DONE.md](WHAT_WAS_DONE.md)** - O que foi feito

## 🛑 Para Parar

```bash
./STOP_APP.sh
```

## 💡 Dica

Para mais detalhes, veja: **[INDEX.md](INDEX.md)**

---

## 🎯 O Que Você Pode Fazer

### Frontend (http://localhost:3000)
- ✅ Login/Logout
- ✅ Ver Dashboard com estatísticas
- ✅ Criar e gerenciar projetos
- ✅ Criar e gerenciar work items
- ✅ Filtrar por status e tipo
- ✅ Buscar em tempo real

### Backend (http://localhost:8086/docs)
- ✅ 35+ endpoints REST
- ✅ Autenticação JWT
- ✅ RBAC com 6 roles
- ✅ Multi-tenancy
- ✅ State machine para work items
- ✅ Rastreabilidade completa

---

## 🔧 Comandos Úteis

```bash
# Iniciar tudo
./RUN_APP.sh

# Parar tudo
./STOP_APP.sh

# Ver logs
tail -f logs/backend.log
tail -f logs/frontend.log

# Resetar banco
docker-compose down -v
docker-compose up -d
sleep 10
uv run alembic upgrade head
make seed
```

---

**Pronto para começar!** 🎉
