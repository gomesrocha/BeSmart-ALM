# 🚨 Solução para Problema de Login

## 🎯 Problema

O login está falhando com erro 401: "Incorrect email or password"

## ✅ Correções Aplicadas

1. **web_ui.py** - Agora retorna erro imediato em vez de usar mock-token
2. **bsmart_client.py** - URLs corrigidas (sem duplicação)

## 🔧 Como Resolver

### Opção 1: Resetar Senha do admin@test.com

```bash
cd /home/fabio/organizacao/repository/bsmart-alm
python scripts/reset_admin_test_password.py
```

Isso vai resetar a senha para: `admin123`

### Opção 2: Usar outro usuário

Tente com o usuário `gomesrocha@gmail.com`:

```bash
cd services/ai_orchestrator
python test_login_credentials.py http://localhost:8086/api/v1 gomesrocha@gmail.com SENHA_AQUI
```

### Opção 3: Verificar senhas existentes

```bash
cd /home/fabio/organizacao/repository/bsmart-alm
python scripts/check_users.py
```

Usuários disponíveis:
- `admin@test.com`
- `gomesrocha@gmail.com`
- `acme@acme.com`
- `odair@acme.com`

## 🚀 Depois de Resetar a Senha

1. **Reinicie o servidor AI Orchestrator**:
```bash
cd services/ai_orchestrator
# Ctrl+C para parar
uv run python start_web.py
```

2. **Abra o browser**: `http://localhost:5010`

3. **Faça login com**:
   - Email: `admin@test.com`
   - Password: `admin123`
   - API URL: `http://localhost:8086/api/v1`

4. **Você deve ver**:
   - ✅ Login successful
   - ✅ Projetos reais do banco de dados

## 📋 Teste Rápido

Teste o login direto na API:

```bash
curl -X POST http://localhost:8086/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}'
```

Se retornar um token, a senha está correta!

## ⚠️ Se Ainda Não Funcionar

1. Verifique se o backend está rodando:
```bash
curl http://localhost:8086/api/v1/health
```

2. Verifique os logs do backend para ver o erro exato

3. Tente criar um novo usuário:
```bash
python scripts/create_test_users.py
```

---

**EXECUTE O SCRIPT DE RESET E TESTE NOVAMENTE!** 🚀
