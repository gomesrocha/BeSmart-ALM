# 🚀 Instruções para Login no AI Orchestrator

## ✅ Correções Aplicadas

1. **URLs corrigidas** - Removida duplicação de `/api/v1`
2. **Autenticação corrigida** - Sistema agora retorna erro quando login falha (não usa mock-token)
3. **Servidor atualizado** - Reinicie para aplicar as mudanças

## 🔑 Resetar Senha do Usuário

Execute este comando para resetar a senha do `admin@test.com`:

```bash
cd /home/fabio/organizacao/repository/bsmart-alm
uv run python scripts/reset_admin_test_password.py
```

Isso vai definir a senha como `admin123`.

## 🧪 Testar Login

Depois de resetar a senha, teste o login:

```bash
cd services/ai_orchestrator
uv run python test_login_credentials.py http://localhost:8086/api/v1 admin@test.com admin123
```

Você deve ver:
```
✅ Login successful!
   Token: eyJhbGciOiJIUzI1NiIs...
✅ Got X projects!
```

## 🌐 Usar no Browser

1. **Reinicie o servidor** (se ainda não fez):
   ```bash
   cd services/ai_orchestrator
   # Ctrl+C para parar
   uv run python start_web.py
   ```

2. **Abra o browser**: `http://localhost:5010`

3. **Faça login** com:
   - **API URL**: `http://localhost:8086/api/v1`
   - **Email**: `admin@test.com`
   - **Password**: `admin123`

4. **Veja os projetos reais** aparecerem!

## 📋 Usuários Disponíveis

| Email | Senha (após reset) | Tipo |
|-------|-------------------|------|
| admin@test.com | admin123 | Super Admin |
| gomesrocha@gmail.com | (precisa resetar) | Super Admin |
| acme@acme.com | (precisa resetar) | Tenant Admin |
| odair@acme.com | (precisa resetar) | Tenant User |

## ⚠️ Troubleshooting

### Erro: "Incorrect email or password"
✅ Execute o script de reset de senha acima

### Erro: "Cannot connect to API"
✅ Verifique se o backend está rodando:
```bash
curl http://localhost:8086/api/v1/health
```

### Erro: "Could not validate credentials"
✅ Token inválido - faça logout e login novamente

## 🎯 Próximos Passos

1. ✅ Resetar senha: `uv run python scripts/reset_admin_test_password.py`
2. ✅ Testar login: `uv run python test_login_credentials.py ...`
3. ✅ Reiniciar servidor: `uv run python start_web.py`
4. ✅ Fazer login no browser
5. ✅ Ver projetos reais!

---

**EXECUTE O RESET DE SENHA E TESTE!** 🚀
