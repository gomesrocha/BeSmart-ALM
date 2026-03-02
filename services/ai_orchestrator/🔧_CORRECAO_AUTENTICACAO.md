# 🔧 Correção de Autenticação

## 🎯 Problema Identificado

O sistema estava usando um `mock-token` quando o login falhava, causando erro 401 ao buscar projetos:

```
❌ Login failed (401): "Incorrect email or password"
❌ Token inválido (401): "Could not validate credentials"
```

## ✅ Correção Aplicada

Agora o sistema **retorna erro imediatamente** quando o login falha, em vez de usar um token mock inválido.

### Antes:
```python
if response.status_code == 200:
    token = data.get('access_token', 'temp-token')
else:
    token = "mock-token"  # ❌ Token inválido!
```

### Depois:
```python
if response.status_code == 200:
    token = data.get('access_token')
    if not token:
        raise HTTPException(status_code=500, detail="No access token in response")
else:
    # ✅ Retorna erro ao usuário
    raise HTTPException(status_code=response.status_code, detail=f"Login failed: {error_detail}")
```

## 🔍 Como Testar as Credenciais

### 1. Verificar Usuários no Banco

```bash
cd /home/fabio/organizacao/repository/bsmart-alm
python scripts/check_users.py
```

### 2. Testar Login Direto

```bash
cd services/ai_orchestrator
python test_login_credentials.py http://localhost:8086/api/v1 SEU_EMAIL SUA_SENHA
```

Exemplo:
```bash
python test_login_credentials.py http://localhost:8086/api/v1 admin@bsmart.com admin123
```

### 3. Resetar Senha (se necessário)

```bash
cd /home/fabio/organizacao/repository/bsmart-alm
python scripts/reset_acme_password.py
```

## 🚀 Próximos Passos

1. **Reinicie o servidor** (Ctrl+C e depois `uv run python start_web.py`)
2. **Verifique suas credenciais** usando o script de teste
3. **Faça login** com as credenciais corretas
4. **Veja os projetos reais** aparecerem!

## 📋 Credenciais Comuns

Verifique se você está usando uma destas:

| Email | Senha | Tipo |
|-------|-------|------|
| admin@bsmart.com | admin123 | Super Admin |
| acme@acme.com | acme123 | Tenant Admin |
| gomesrocha@bsmart.com | gomes123 | Super Admin |

## ⚠️ Mensagens de Erro

### "Incorrect email or password"
- ✅ Verifique o email e senha
- ✅ Use o script `check_users.py` para ver usuários disponíveis
- ✅ Use o script `reset_acme_password.py` para resetar senha

### "Could not validate credentials"
- ✅ Token inválido ou expirado
- ✅ Faça logout e login novamente

### "Cannot connect to API"
- ✅ Verifique se o backend está rodando em `http://localhost:8086`
- ✅ Teste com: `curl http://localhost:8086/api/v1/health`

---

**REINICIE O SERVIDOR E TESTE COM CREDENCIAIS CORRETAS!** 🚀
