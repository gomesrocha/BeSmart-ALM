# 🌐 Configuração de Acesso pela Rede Local

## ✅ Configurações Aplicadas

### 1. Frontend (Vite)
**Arquivo**: `frontend/vite.config.ts`

```typescript
server: {
  host: '0.0.0.0', // Aceita conexões de qualquer IP
  port: 3000,
  strictPort: false,
  proxy: {
    '/api': {
      target: 'http://localhost:8086',
      changeOrigin: true,
      secure: false,
      ws: true,
    },
  },
}
```

### 2. Backend (FastAPI)
**Arquivo**: `.env`

```bash
CORS_ORIGINS=["*"]  # Aceita requisições de qualquer origem
```

---

## 🚀 Como Iniciar o Sistema

### 1. Parar Serviços Atuais (se estiverem rodando)
```bash
# Parar frontend (Ctrl+C no terminal)
# Parar backend (Ctrl+C no terminal)
```

### 2. Iniciar Backend
```bash
# Terminal 1
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086
```

### 3. Iniciar Frontend
```bash
# Terminal 2
cd frontend
npm run dev
```

---

## 📱 Como Acessar de Outros Dispositivos

### Seu IP na Rede Local:
```
192.168.3.189
```

### URLs de Acesso:

#### Frontend:
```
http://192.168.3.189:3000
```

#### Backend (API):
```
http://192.168.3.189:8086
```

#### Documentação da API (Swagger):
```
http://192.168.3.189:8086/docs
```

---

## 🧪 Teste de Conectividade

### Do seu computador:
```bash
# Teste o frontend
curl http://192.168.3.189:3000

# Teste o backend
curl http://192.168.3.189:8086/api/health
```

### De outro dispositivo na mesma rede:
1. Abra o navegador
2. Acesse: `http://192.168.3.189:3000`
3. Faça login normalmente

---

## 🔥 Firewall (Se necessário)

Se ainda não conseguir acessar, pode ser o firewall:

### Ubuntu/Debian:
```bash
# Permitir porta 3000 (frontend)
sudo ufw allow 3000/tcp

# Permitir porta 8086 (backend)
sudo ufw allow 8086/tcp

# Verificar status
sudo ufw status
```

### Fedora/RHEL:
```bash
# Permitir porta 3000
sudo firewall-cmd --add-port=3000/tcp --permanent

# Permitir porta 8086
sudo firewall-cmd --add-port=8086/tcp --permanent

# Recarregar
sudo firewall-cmd --reload
```

---

## 📋 Checklist de Verificação

- [ ] Backend rodando com `--host 0.0.0.0`
- [ ] Frontend rodando (vite.config.ts com host: '0.0.0.0')
- [ ] CORS configurado para aceitar qualquer origem
- [ ] Firewall permite portas 3000 e 8086
- [ ] Dispositivos na mesma rede Wi-Fi/LAN
- [ ] IP correto (192.168.3.189)

---

## 🐛 Troubleshooting

### Problema: "Connection refused"
**Solução**:
```bash
# Verificar se serviços estão rodando
netstat -tulpn | grep 3000
netstat -tulpn | grep 8086

# Reiniciar com host correto
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086
```

### Problema: "CORS error"
**Solução**:
```bash
# Verificar .env
cat .env | grep CORS

# Deve mostrar:
# CORS_ORIGINS=["*"]

# Reiniciar backend após mudança
```

### Problema: "Cannot GET /"
**Solução**:
```bash
# Frontend não está rodando
cd frontend
npm run dev

# Verificar se aparece:
# ➜  Local:   http://localhost:3000/
# ➜  Network: http://192.168.3.189:3000/
```

### Problema: Vite mostra "blocked request"
**Solução**:
```bash
# Parar frontend (Ctrl+C)
# Limpar cache
rm -rf frontend/node_modules/.vite

# Reiniciar
cd frontend
npm run dev
```

---

## 📱 Testando de Celular/Tablet

1. Conecte o dispositivo na mesma rede Wi-Fi
2. Abra o navegador
3. Digite: `http://192.168.3.189:3000`
4. Faça login:
   - Email: `admin@example.com`
   - Senha: `admin123`

---

## 🔒 Segurança (Importante!)

⚠️ **ATENÇÃO**: A configuração `CORS_ORIGINS=["*"]` é apenas para desenvolvimento!

Para produção, configure origens específicas:
```bash
CORS_ORIGINS=["http://192.168.3.189:3000","http://seu-dominio.com"]
```

---

## 📊 Comandos Úteis

### Ver IP da máquina:
```bash
hostname -I
# ou
ip addr show
```

### Ver portas em uso:
```bash
netstat -tulpn | grep LISTEN
```

### Testar conectividade:
```bash
# Do próprio servidor
curl http://192.168.3.189:3000
curl http://192.168.3.189:8086/api/health

# De outro dispositivo
ping 192.168.3.189
```

---

## 🎯 Resumo Rápido

```bash
# 1. Iniciar Backend
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086

# 2. Iniciar Frontend (outro terminal)
cd frontend && npm run dev

# 3. Acessar de qualquer dispositivo na rede
http://192.168.3.189:3000
```

---

**Data**: 24/02/2026  
**IP Local**: 192.168.3.189  
**Status**: ✅ Configurado para acesso na rede local
