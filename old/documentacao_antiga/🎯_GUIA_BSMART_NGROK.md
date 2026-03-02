# 🎯 Guia Bsmart-ALM com ngrok

## 🚀 Uso Simples (1 Comando!)

```bash
./start_bsmart.sh
```

Aguarde ~15 segundos e pronto! 🎉

---

## 🌐 Seus Domínios

- **Frontend**: https://bsmart.ngrok.app
- **Backend**: https://projectmanager.ngrok.app

---

## 📋 O Que o Script Faz

1. ✅ Configura frontend para usar o backend correto
2. ✅ Inicia backend na porta 8086
3. ✅ Cria túnel ngrok: projectmanager.ngrok.app → backend
4. ✅ Inicia frontend na porta 3000
5. ✅ Cria túnel ngrok: bsmart.ngrok.app → frontend
6. ✅ Salva informações em `bsmart_urls.txt`

---

## 📱 Para Compartilhar

Envie para seus colegas:

```
🌐 Teste o Bsmart-ALM!

URL: https://bsmart.ngrok.app

Login:
- Email: admin@example.com
- Senha: admin123

Obs: Clique em "Visit Site" se o ngrok mostrar aviso.
```

---

## 🛑 Para Parar

Pressione `Ctrl+C` no terminal.

Isso para:
- Backend
- Frontend  
- Ambos túneis ngrok

---

## 📊 Monitoramento

Dashboards do ngrok:
- **Backend**: http://localhost:4040
- **Frontend**: http://localhost:4041

Veja todas as requisições em tempo real!

---

## 📝 Logs

Se algo der errado:

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

## 🔧 Configuração Automática

O script cria automaticamente `frontend/.env`:

```bash
VITE_API_URL=https://projectmanager.ngrok.app/api/v1
```

Frontend se conecta automaticamente ao backend! ✨

---

## ✅ Checklist

Antes de executar:
- [ ] ngrok instalado (`sudo snap install ngrok`)
- [ ] ngrok autenticado (`ngrok config add-authtoken TOKEN`)
- [ ] Domínios configurados no dashboard do ngrok:
  - [ ] projectmanager.ngrok.app
  - [ ] bsmart.ngrok.app

---

## 🎉 Resultado Esperado

```
🚀 Iniciando Bsmart-ALM...

✅ ngrok instalado

⚙️  Configurando Frontend...
✅ Frontend configurado para usar: https://projectmanager.ngrok.app/api/v1

📦 Iniciando Backend...
   PID: 12345
✅ Backend rodando na porta 8086

🌐 Criando túnel ngrok para Backend...
   Domínio: projectmanager.ngrok.app
✅ Backend acessível em: https://projectmanager.ngrok.app

🎨 Iniciando Frontend...
   PID: 12346
✅ Frontend rodando na porta 3000

🌐 Criando túnel ngrok para Frontend...
   Domínio: bsmart.ngrok.app
✅ Frontend acessível em: https://bsmart.ngrok.app

╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              🎉 Bsmart-ALM Iniciado! 🎉                   ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

📱 Compartilhe com seus colegas:

🌐 Frontend: https://bsmart.ngrok.app
🔧 Backend:  https://projectmanager.ngrok.app

🔑 Credenciais:
   Email: admin@example.com
   Senha: admin123

📊 Dashboards ngrok:
   Backend:  http://localhost:4040
   Frontend: http://localhost:4041

📝 Informações salvas em: bsmart_urls.txt

✨ Sistema pronto para uso!

Pressione Ctrl+C para parar todos os serviços
```

---

## 🐛 Troubleshooting

### Erro: "Failed to start tunnel"
**Causa**: Domínios não configurados no ngrok  
**Solução**: Configure os domínios no dashboard do ngrok

### Erro: "Port already in use"
**Solução**:
```bash
sudo lsof -ti:8086 | xargs kill -9
sudo lsof -ti:3000 | xargs kill -9
```

### Erro: "ngrok not authenticated"
**Solução**:
```bash
ngrok config add-authtoken SEU_TOKEN
```

---

## 💡 Vantagens

- ✅ **Domínios fixos**: URLs não mudam
- ✅ **Profissional**: bsmart.ngrok.app é fácil de lembrar
- ✅ **Automático**: Tudo configurado automaticamente
- ✅ **Simples**: 1 comando para iniciar tudo

---

## 🎓 Estrutura

```
Seu Computador
├── Backend (porta 8086)
│   └── ngrok → https://projectmanager.ngrok.app
│
└── Frontend (porta 3000)
    └── ngrok → https://bsmart.ngrok.app
    └── Conecta em: https://projectmanager.ngrok.app/api/v1
```

---

## 🔒 Segurança

⚠️ **Lembre-se**:
- URLs são públicas (qualquer um com a URL pode acessar)
- Use apenas para testes/demos
- Não coloque dados sensíveis
- Mude senhas se necessário

---

## 🎯 Pronto!

Execute e compartilhe:

```bash
./start_bsmart.sh
```

**URLs para compartilhar**:
- Frontend: https://bsmart.ngrok.app
- Login: admin@example.com / admin123

🚀 **Seus colegas podem testar de qualquer lugar do mundo!**

---

**Data**: 24/02/2026  
**Domínios**: bsmart.ngrok.app + projectmanager.ngrok.app  
**Status**: ✅ Pronto para uso
