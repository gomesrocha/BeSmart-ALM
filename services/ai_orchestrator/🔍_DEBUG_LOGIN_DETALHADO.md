# 🔍 Debug de Login Detalhado

## 🎯 Problema

O login está falhando com erro 401, mas as mesmas credenciais funcionam na API diretamente.

```
⚠️ API login failed (status 401): {"detail":"Incorrect email or password"}
```

## ✅ Logs Adicionados

Adicionei logs detalhados para ver exatamente o que está sendo enviado:

```python
logging.info(f"📧 Email: {request.email}")
logging.info(f"🔑 Password length: {len(request.password)} chars")
logging.info(f"📦 Payload: {login_payload}")
```

## 🚀 Como Testar

1. **Reinicie o servidor**:
```bash
cd services/ai_orchestrator
# Ctrl+C
uv run python start_web.py
```

2. **Faça login** no browser (`http://localhost:5010`):
   - Email: `gomesrocha@gmail.com`
   - Password: `gomes1234`
   - API URL: `http://localhost:8086/api/v1`

3. **Verifique os logs** no terminal do servidor

## 📋 Logs Esperados

Você deve ver algo como:

```
🔐 Attempting login to: http://localhost:8086/api/v1/auth/login
📧 Email: gomesrocha@gmail.com
🔑 Password length: 9 chars
📦 Payload: {'email': 'gomesrocha@gmail.com', 'password': 'gomes1234'}
📡 Login response status: 200 ou 401
```

## 🔍 O Que Verificar

1. **Email correto?** - Deve ser exatamente `gomesrocha@gmail.com`
2. **Senha correta?** - Deve ter 9 caracteres (`gomes1234`)
3. **URL correta?** - Deve ser `http://localhost:8086/api/v1/auth/login`

## 🧪 Teste Direto na API

Compare com o teste direto:

```bash
curl -X POST http://localhost:8086/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"gomesrocha@gmail.com","password":"gomes1234"}'
```

Se o curl funciona mas o AI Orchestrator não, pode ser:
- Problema de encoding
- Espaços extras na senha
- Problema no frontend enviando dados errados

## 📝 Próximos Passos

Depois de ver os logs, saberemos:
1. Se o email/senha estão sendo enviados corretamente
2. Se a URL está correta
3. Qual é a resposta exata da API

---

**REINICIE O SERVIDOR E TESTE NOVAMENTE!** 🚀
