# 🌍 Configuração com Ngrok - Acesso Externo

## 🎯 Objetivo

Expor o sistema Bsmart-ALM para a internet usando ngrok, permitindo que colegas testem de qualquer lugar.

---

## 📋 Pré-requisitos

### 1. Instalar ngrok
```bash
# Ubuntu/Debian
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Ou via snap
sudo snap install ngrok

# Ou download direto
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

### 2. Criar conta no ngrok (gratuita)
```
https://dashboard.ngrok.com/signup
```

### 3. Autenticar ngrok
```bash
# Após criar conta, copie seu authtoken do dashboard
ngrok config add-authtoken SEU_TOKEN_AQUI
```

---

## 🚀 Configuração Passo a Passo

### Passo 1: Atualizar CORS no Backend

O backend já está configurado para aceitar qualquer origem:
```bash
# .env já tem:
CORS_ORIGINS=["*"]
```

✅ Já configurado!

---

### Passo 2: Iniciar os Serviços

#### Terminal 1 - Backend:
```bash
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086
```

#### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

Aguarde o frontend iniciar e anote a porta (geralmente 3000).

---

### Passo 3: Criar Túneis ngrok

#### Terminal 3 - Túnel para Frontend:
```bash
ngrok http 3000
```

Você verá algo assim:
```
Session Status                online
Account                       seu-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:3000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Copie a URL do Forwarding**: `https://abc123.ngrok-free.app`

#### Terminal 4 - Túnel para Backend:
```bash
ngrok http 8086
```

Você verá:
```
Forwarding                    https://xyz789.ngrok-free.app -> http://localhost:8086
```

**Copie a URL do Forwarding**: `https://xyz789.ngrok-free.app`

---

### Passo 4: Atualizar Configuração do Frontend

Agora precisamos configurar o frontend para usar a URL do backend do ngrok.

**Opção A: Variável de Ambiente (Recomendado)**

Crie/edite `frontend/.env`:
```bash
VITE_API_URL=https://xyz789.ngrok-free.app
```

E atualize `frontend/src/api/client.ts`:
```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8086',
  headers: {
    'Content-Type': 'application/json',
  },
})

// ... resto do código
```

**Opção B: Configuração Direta (Mais Rápido para Teste)**

Edite `frontend/src/api/client.ts` temporariamente:
```typescript
const api = axios.create({
  baseURL: 'https://xyz789.ngrok-free.app', // Sua URL do ngrok
  headers: {
    'Content-Type': 'application/json',
  },
})
```

Depois reinicie o frontend:
```bash
# Ctrl+C no terminal do frontend
cd frontend
npm run dev
```

---

## 🎉 Compartilhar com Colegas

### URLs para Compartilhar:

**Frontend (Interface):**
```
https://abc123.ngrok-free.app
```

**Credenciais de Teste:**
```
Email: admin@example.com
Senha: admin123
```

### Instruções para os Colegas:

```
1. Acesse: https://abc123.ngrok-free.app
2. Clique em "Visit Site" (ngrok mostra aviso de segurança)
3. Faça login com:
   - Email: admin@example.com
   - Senha: admin123
4. Teste as funcionalidades!
```

---

## 🔧 Configuração Avançada (Opcional)

### Usar Domínio Customizado (Plano Pago)

Se tiver plano pago do ngrok:
```bash
ngrok http 3000 --domain=seu-dominio.ngrok.app
ngrok http 8086 --domain=api-seu-dominio.ngrok.app
```

### Configurar ngrok.yml

Crie `~/.ngrok2/ngrok.yml`:
```yaml
version: "2"
authtoken: SEU_TOKEN_AQUI

tunnels:
  frontend:
    proto: http
    addr: 3000
    inspect: true
  
  backend:
    proto: http
    addr: 8086
    inspect: true
```

Depois inicie ambos:
```bash
ngrok start --all
```

---

## 📊 Monitoramento

### Dashboard Web do ngrok:
```
http://localhost:4040
```

Aqui você pode ver:
- Todas as requisições
- Tempo de resposta
- Erros
- Replay de requisições

---

## 🐛 Troubleshooting

### Problema: "ERR_NGROK_3200"
**Causa**: Túnel expirou (plano gratuito tem limite de tempo)  
**Solução**: Reinicie o ngrok

### Problema: "CORS error" mesmo com CORS=*
**Causa**: Frontend ainda está usando localhost  
**Solução**: Verifique se atualizou o baseURL no client.ts

### Problema: "Failed to fetch"
**Causa**: Backend não está acessível  
**Solução**: 
```bash
# Verificar se backend está rodando
curl http://localhost:8086/api/health

# Verificar túnel ngrok
curl https://xyz789.ngrok-free.app/api/health
```

### Problema: Página em branco
**Causa**: Frontend não encontra o backend  
**Solução**: Verifique console do navegador (F12) e atualize baseURL

---

## 🔒 Segurança

### ⚠️ Importante:

1. **Não use em produção**: ngrok é para testes/desenvolvimento
2. **Mude as senhas**: Use senhas fortes para testes externos
3. **Monitore acessos**: Use o dashboard do ngrok
4. **Limite de tempo**: Túneis gratuitos expiram após 2 horas
5. **Dados sensíveis**: Não coloque dados reais durante testes

### Criar Usuário de Teste:

```bash
# Acesse o sistema e crie usuários específicos para teste
# Ou use o script de seed com dados de teste
```

---

## 📝 Checklist de Configuração

- [ ] ngrok instalado e autenticado
- [ ] Backend rodando (porta 8086)
- [ ] Frontend rodando (porta 3000)
- [ ] Túnel ngrok para frontend criado
- [ ] Túnel ngrok para backend criado
- [ ] Frontend configurado com URL do backend ngrok
- [ ] CORS configurado para aceitar qualquer origem
- [ ] Testado acesso pela URL do ngrok
- [ ] URLs compartilhadas com colegas

---

## 🎯 Comandos Resumidos

```bash
# Terminal 1 - Backend
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086

# Terminal 2 - Frontend
cd frontend && npm run dev

# Terminal 3 - ngrok Frontend
ngrok http 3000

# Terminal 4 - ngrok Backend
ngrok http 8086

# Atualizar frontend/src/api/client.ts com URL do backend ngrok
# Reiniciar frontend
# Compartilhar URL do frontend ngrok com colegas
```

---

## 📱 Teste de Diferentes Dispositivos

Seus colegas podem testar de:
- ✅ Computadores (Windows, Mac, Linux)
- ✅ Celulares (Android, iOS)
- ✅ Tablets
- ✅ Qualquer lugar do mundo com internet

---

## 💡 Dicas

1. **Mantenha os terminais abertos**: Fechar fecha os túneis
2. **Use o dashboard**: http://localhost:4040 para debug
3. **Avise sobre o aviso**: ngrok mostra tela de aviso, é só clicar "Visit Site"
4. **Anote as URLs**: Elas mudam cada vez que reinicia o ngrok
5. **Plano gratuito**: Limite de 1 túnel por vez (use 2 terminais)

---

**Data**: 24/02/2026  
**Status**: ✅ Pronto para ngrok  
**Próximo Passo**: Iniciar túneis e compartilhar URLs
