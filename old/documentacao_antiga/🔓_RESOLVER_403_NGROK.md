# 🔓 Resolver 403 Forbidden - ngrok

## 🎯 Problema

Você está vendo **403 Forbidden** porque o ngrok gratuito mostra uma página de aviso antes de permitir acesso.

```
HTTP Requests
-------------
GET /                          403 Forbidden
GET /favicon.ico               403 Forbidden
```

## ✅ Solução Simples

### Para Você (Testando Localmente):

Quando acessar a URL do ngrok, você verá uma tela assim:

```
┌─────────────────────────────────────────┐
│                                         │
│  ⚠️  You are about to visit:           │
│                                         │
│  https://skylar-glacial-brainily...    │
│                                         │
│  This site is served for free through  │
│  ngrok.com                             │
│                                         │
│     [Visit Site]    [Learn More]       │
│                                         │
└─────────────────────────────────────────┘
```

**Clique em "Visit Site"** e pronto! ✅

### Para Seus Colegas:

Avise-os para clicar em **"Visit Site"** na primeira vez que acessarem.

---

## 🚀 Solução Automática (Script)

Criei um script que configura tudo automaticamente!

### Uso:

```bash
# 1. Certifique-se que backend e frontend estão rodando

# Terminal 1 - Backend
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086

# Terminal 2 - Frontend  
cd frontend && npm run dev

# Terminal 3 - Script ngrok
./start_ngrok.sh
```

O script vai:
1. ✅ Criar túnel para backend
2. ✅ Criar túnel para frontend
3. ✅ Atualizar automaticamente o frontend/.env
4. ✅ Mostrar as URLs para compartilhar
5. ✅ Salvar URLs em ngrok_urls.txt

---

## 📋 Passo a Passo Manual (Se Preferir)

### 1. Iniciar Backend
```bash
# Terminal 1
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086
```

### 2. Criar Túnel Backend
```bash
# Terminal 2
ngrok http 8086
```

Copie a URL: `https://xyz789.ngrok-free.app`

### 3. Configurar Frontend
```bash
# Atualizar .env com a URL do backend
echo 'VITE_API_URL=https://xyz789.ngrok-free.app/api/v1' > frontend/.env
```

### 4. Iniciar Frontend
```bash
# Terminal 3
cd frontend
npm run dev
```

### 5. Criar Túnel Frontend
```bash
# Terminal 4
ngrok http 3000
```

Copie a URL: `https://abc123.ngrok-free.app`

### 6. Compartilhar
```
URL: https://abc123.ngrok-free.app
Login: admin@example.com
Senha: admin123

⚠️ Avise para clicar em "Visit Site" na primeira vez!
```

---

## 🔧 Alternativa: Desabilitar Aviso (Plano Pago)

Se tiver plano pago do ngrok, pode desabilitar o aviso:

```bash
ngrok http 3000 --domain=seu-dominio.ngrok.app
```

---

## 🐛 Outros Problemas Comuns

### Problema: "ERR_NGROK_3200"
**Causa**: Túnel expirou  
**Solução**: Reinicie o ngrok

### Problema: Frontend não conecta ao backend
**Causa**: frontend/.env não foi atualizado  
**Solução**: 
```bash
# Verificar
cat frontend/.env

# Deve mostrar:
# VITE_API_URL=https://sua-url-backend.ngrok-free.app/api/v1

# Se não, atualize e reinicie frontend
```

### Problema: Página em branco
**Causa**: CORS ou URL incorreta  
**Solução**:
```bash
# 1. Verificar CORS no .env
cat .env | grep CORS
# Deve ter: CORS_ORIGINS=["*"]

# 2. Verificar console do navegador (F12)
# 3. Verificar se backend está acessível:
curl https://sua-url-backend.ngrok-free.app/api/health
```

---

## 📊 Verificar Status

### Dashboard ngrok:
```
Backend:  http://localhost:4040
Frontend: http://localhost:4041
```

Aqui você vê todas as requisições em tempo real.

### Testar Conectividade:
```bash
# Testar backend
curl https://sua-url-backend.ngrok-free.app/api/health

# Deve retornar algo como:
# {"status":"ok"}
```

---

## 💡 Dicas

1. **Mantenha terminais abertos**: Fechar fecha os túneis
2. **Use o script**: Automatiza tudo
3. **Salve as URLs**: Elas mudam ao reiniciar
4. **Avise sobre o aviso**: Colegas precisam clicar "Visit Site"
5. **Monitore**: Use os dashboards para debug

---

## 🎯 Resumo

```
Problema: 403 Forbidden
Causa: Página de aviso do ngrok (plano gratuito)
Solução: Clicar em "Visit Site"

Automação: ./start_ngrok.sh
Manual: Seguir passo a passo acima
```

---

**Data**: 24/02/2026  
**Status**: ✅ Problema identificado e resolvido  
**Solução**: Script automático criado
