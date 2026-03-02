# 🎯 ngrok Automático - Setup Completo

## ✨ Solução Automática

Criei um script que faz TUDO automaticamente:
- ✅ Inicia backend
- ✅ Cria túnel ngrok para backend
- ✅ Configura frontend com URL do backend
- ✅ Inicia frontend
- ✅ Cria túnel ngrok para frontend
- ✅ Mostra URLs para compartilhar

---

## 🚀 Uso Rápido (1 comando!)

```bash
./start_with_ngrok.sh
```

Aguarde ~15 segundos e pronto! 🎉

---

## 📋 Pré-requisitos

### 1. Instalar ngrok
```bash
sudo snap install ngrok
```

### 2. Autenticar ngrok
```bash
# Pegue seu token em: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken SEU_TOKEN_AQUI
```

### 3. Pronto!
```bash
./start_with_ngrok.sh
```

---

## 📱 O Que Você Verá

```
🚀 Iniciando Bsmart-ALM com ngrok...

✅ ngrok instalado e autenticado

📦 Iniciando Backend...
   PID: 12345
✅ Backend rodando

🌐 Criando túnel ngrok para Backend...
✅ Backend ngrok URL: https://abc123.ngrok-free.app

⚙️  Configurando Frontend...
✅ Frontend configurado

🎨 Iniciando Frontend...
   PID: 12346
✅ Frontend rodando

🌐 Criando túnel ngrok para Frontend...
✅ Frontend ngrok URL: https://xyz789.ngrok-free.app

╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              🎉 Sistema Iniciado com Sucesso! 🎉          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

📱 Compartilhe com seus colegas:

Frontend: https://xyz789.ngrok-free.app
Backend:  https://abc123.ngrok-free.app

🔑 Credenciais:
   Email: admin@example.com
   Senha: admin123

📊 Dashboards:
   ngrok Backend:  http://localhost:4040
   ngrok Frontend: http://localhost:4041

📝 URLs salvas em: ngrok_urls.txt

Pressione Ctrl+C para parar todos os serviços
```

---

## 📄 Arquivo ngrok_urls.txt

O script cria automaticamente um arquivo com as URLs:

```
🌐 URLs do ngrok - Bsmart-ALM
================================

Frontend (Interface):
https://xyz789.ngrok-free.app

Backend (API):
https://abc123.ngrok-free.app

Credenciais de Teste:
Email: admin@example.com
Senha: admin123

================================
Gerado em: Mon Feb 24 15:30:00 2026
```

Você pode copiar e colar esse arquivo para seus colegas!

---

## 🎯 Para Compartilhar

Basta enviar para seus colegas:

```
Olá! Teste o Bsmart-ALM:

URL: https://xyz789.ngrok-free.app

Login:
- Email: admin@example.com
- Senha: admin123

Obs: Clique em "Visit Site" quando o ngrok mostrar o aviso.
```

---

## 🛑 Para Parar

Pressione `Ctrl+C` no terminal onde o script está rodando.

Isso vai parar:
- Backend
- Frontend
- Ambos túneis ngrok

---

## 🔍 Logs

Se algo der errado, verifique os logs:

```bash
# Backend
cat logs/backend.log

# Frontend
cat logs/frontend.log

# ngrok Backend
cat logs/ngrok_backend.log

# ngrok Frontend
cat logs/ngrok_frontend.log
```

---

## 🐛 Troubleshooting

### Problema: "ngrok não está instalado"
```bash
sudo snap install ngrok
```

### Problema: "ngrok não está autenticado"
```bash
ngrok config add-authtoken SEU_TOKEN
```

### Problema: "Porta já em uso"
```bash
# Parar processos nas portas
sudo lsof -ti:8086 | xargs kill -9
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:4040 | xargs kill -9
sudo lsof -ti:4041 | xargs kill -9
```

### Problema: Script não executa
```bash
chmod +x start_with_ngrok.sh
```

---

## 💡 Vantagens desta Solução

1. ✅ **Automático**: Um único comando
2. ✅ **URLs Dinâmicas**: Frontend e backend com URLs próprias
3. ✅ **Auto-configuração**: Frontend se configura automaticamente
4. ✅ **Arquivo de URLs**: Fácil de compartilhar
5. ✅ **Logs Separados**: Fácil debug
6. ✅ **Cleanup**: Ctrl+C para tudo

---

## 🎓 Como Funciona

1. Script inicia backend na porta 8086
2. Cria túnel ngrok para backend (porta 4040)
3. Extrai URL do backend do ngrok
4. Cria `frontend/.env` com URL do backend
5. Inicia frontend na porta 3000
6. Cria túnel ngrok para frontend (porta 4041)
7. Extrai URL do frontend do ngrok
8. Salva ambas URLs em `ngrok_urls.txt`
9. Mostra resumo bonito no terminal

---

## 📊 Dashboards ngrok

Acesse para ver requisições em tempo real:

- **Backend**: http://localhost:4040
- **Frontend**: http://localhost:4041

---

## 🔒 Segurança

⚠️ **Lembre-se**:
- URLs do ngrok são públicas
- Qualquer pessoa com a URL pode acessar
- Use apenas para testes/demos
- Não coloque dados sensíveis
- Mude as senhas padrão se necessário

---

## 🎉 Pronto!

Agora é só executar:

```bash
./start_with_ngrok.sh
```

E compartilhar a URL com seus colegas! 🚀

---

**Data**: 24/02/2026  
**Status**: ✅ Script Automático Criado  
**Tempo de Setup**: ~15 segundos
