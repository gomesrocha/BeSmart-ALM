# ⚡ Setup Rápido - ngrok

## 🚀 Passo a Passo (5 minutos)

### 1️⃣ Instalar ngrok
```bash
# Snap (mais fácil)
sudo snap install ngrok

# Ou download direto
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

### 2️⃣ Autenticar
```bash
# Crie conta em: https://dashboard.ngrok.com/signup
# Copie seu authtoken e execute:
ngrok config add-authtoken SEU_TOKEN_AQUI
```

### 3️⃣ Iniciar Backend
```bash
# Terminal 1
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086
```

### 4️⃣ Criar Túnel Backend
```bash
# Terminal 2
ngrok http 8086
```

**Copie a URL**: `https://xyz789.ngrok-free.app`

### 5️⃣ Configurar Frontend
```bash
# Criar arquivo de ambiente
echo 'VITE_API_URL=https://xyz789.ngrok-free.app/api/v1' > frontend/.env

# Substitua xyz789.ngrok-free.app pela SUA URL do ngrok!
```

### 6️⃣ Iniciar Frontend
```bash
# Terminal 3
cd frontend
npm run dev
```

### 7️⃣ Criar Túnel Frontend
```bash
# Terminal 4
ngrok http 3000
```

**Copie a URL**: `https://abc123.ngrok-free.app`

---

## 🎉 Pronto! Compartilhe:

```
URL: https://abc123.ngrok-free.app
Login: admin@example.com
Senha: admin123
```

---

## 📋 Checklist Visual

```
✅ ngrok instalado
✅ ngrok autenticado
✅ Backend rodando (Terminal 1)
✅ Túnel backend criado (Terminal 2)
✅ frontend/.env criado com URL do backend
✅ Frontend rodando (Terminal 3)
✅ Túnel frontend criado (Terminal 4)
✅ URL compartilhada com colegas
```

---

## 🐛 Problema Comum

### Frontend não conecta ao backend?

**Verifique o arquivo `frontend/.env`:**
```bash
cat frontend/.env
```

Deve mostrar:
```
VITE_API_URL=https://xyz789.ngrok-free.app/api/v1
```

**Se não existir, crie:**
```bash
echo 'VITE_API_URL=https://SUA-URL-NGROK-BACKEND/api/v1' > frontend/.env
```

**Depois reinicie o frontend** (Ctrl+C e `npm run dev`)

---

## 💡 Dica Importante

⚠️ **Sempre que reiniciar o ngrok, a URL muda!**

Você precisará:
1. Copiar a nova URL do backend
2. Atualizar `frontend/.env`
3. Reiniciar o frontend

---

## 🎯 Comandos em Ordem

```bash
# 1. Backend
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086

# 2. Túnel Backend (outro terminal)
ngrok http 8086
# Copie a URL: https://xyz789.ngrok-free.app

# 3. Configure Frontend
echo 'VITE_API_URL=https://xyz789.ngrok-free.app/api/v1' > frontend/.env

# 4. Frontend (outro terminal)
cd frontend && npm run dev

# 5. Túnel Frontend (outro terminal)
ngrok http 3000
# Copie a URL: https://abc123.ngrok-free.app

# 6. Compartilhe a URL do frontend com colegas!
```

---

**Tempo Total**: ~5 minutos  
**Terminais Necessários**: 4  
**Status**: ✅ Pronto para compartilhar
