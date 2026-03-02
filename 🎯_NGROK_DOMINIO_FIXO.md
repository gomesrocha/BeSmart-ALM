# 🎯 ngrok com Domínio Fixo

## 📋 Para Domínios Customizados do ngrok

Se você tem um domínio fixo do ngrok (ex: `gomesrocha.ngrok.app`), siga este guia.

---

## 🚀 Setup Manual

### 1. Iniciar Backend
```bash
# Terminal 1
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086
```

### 2. Criar Túnel Backend com Domínio Fixo
```bash
# Terminal 2
ngrok http 8086 --domain=backend.gomesrocha.ngrok.app
```

### 3. Configurar Frontend
```bash
# Criar/editar frontend/.env
echo 'VITE_API_URL=https://backend.gomesrocha.ngrok.app/api/v1' > frontend/.env
```

### 4. Iniciar Frontend
```bash
# Terminal 3
cd frontend
npm run dev
```

### 5. Criar Túnel Frontend com Domínio Fixo
```bash
# Terminal 4
ngrok http 3000 --domain=frontend.gomesrocha.ngrok.app
```

---

## 📱 URLs para Compartilhar

```
Frontend: https://frontend.gomesrocha.ngrok.app
Backend:  https://backend.gomesrocha.ngrok.app

Login:
Email: admin@example.com
Senha: admin123
```

---

## ✅ Vantagens do Domínio Fixo

- ✅ URLs não mudam ao reiniciar
- ✅ Mais profissional
- ✅ Fácil de lembrar
- ✅ Pode configurar uma vez só

---

## 📝 Aguardando suas URLs...

Me passe as URLs quando estiver pronto:
1. URL do frontend
2. URL do backend

Vou atualizar o código para usar elas! 👍

---

**Status**: ⏳ Aguardando URLs do domínio gomesrocha
