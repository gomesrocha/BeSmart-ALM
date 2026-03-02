# ⚡ Teste Rápido - AI Orchestrator Interfaces

## 🎯 Objetivo

Testar rapidamente as interfaces do AI Orchestrator em 2 minutos.

## 🚀 Teste da Web UI (Recomendado)

### 1. Setup (30 segundos)
```bash
cd services/ai_orchestrator
uv venv
source .venv/bin/activate
uv pip install -e .
```

### 2. Iniciar (10 segundos)
```bash
python start_web.py
```

Você verá:
```
🚀 Starting AI Orchestrator Web UI...
📱 Open http://localhost:8080 in your browser
⏹️  Press Ctrl+C to stop
```

### 3. Testar (1 minuto)
1. Abra http://localhost:8080
2. Faça login:
   - API URL: `http://localhost:8086/api/v1`
   - Email: `admin@acme.com`
   - Password: `admin123`
3. Selecione projeto: "Sistema de Vendas"
4. Clique em "Load Work Items"
5. Selecione work items
6. Clique em "Add to Queue"
7. Veja estatísticas atualizarem

### 4. Parar
```bash
Ctrl+C
```

## 🖥️ Teste da CLI (Alternativo)

### 1. Setup (mesmo acima)
```bash
cd services/ai_orchestrator
source .venv/bin/activate
```

### 2. Iniciar
```bash
python start_cli.py
```

### 3. Testar
```
Choose an option: 1
API URL: http://localhost:8086/api/v1
Email: admin@acme.com
Password: admin123

Choose an option: 2
Select project ID: 1

Choose an option: 3
Add ready items to processing queue? y

Choose an option: 6
# Ver estatísticas

Choose an option: 8
# Sair
```

## ✅ O Que Você Deve Ver

### Web UI
- ✅ Interface visual moderna
- ✅ Login funciona
- ✅ Projetos carregam
- ✅ Work items aparecem
- ✅ Estatísticas atualizam
- ✅ Status em tempo real (WebSocket)

### CLI
- ✅ Menu colorido com emojis
- ✅ Tabelas formatadas
- ✅ Progress bars
- ✅ Validação de entrada
- ✅ Feedback visual

## ⚠️ Notas

- **Dados são simulados**: Login não valida credenciais reais
- **Processamento é simulado**: Não executa agentes de verdade
- **Bsmart-ALM não é necessário**: Para testar apenas as interfaces

## 🐛 Problemas Comuns

### "Module not found"
```bash
uv pip install -e . --force-reinstall
```

### "Port 8080 already in use"
```bash
lsof -i :8080
kill -9 <PID>
```

### "Rich not found"
```bash
uv pip install rich click fastapi uvicorn websockets
```

## 📊 Resultado Esperado

Após o teste, você deve ter visto:
- ✅ Interface funcionando
- ✅ Login simulado
- ✅ Projetos listados
- ✅ Work items carregados
- ✅ Fila atualizada
- ✅ Estatísticas exibidas

## 🎉 Sucesso!

Se tudo funcionou, as interfaces estão prontas!

Próximo passo: Implementar o loop de processamento real.

## 📚 Mais Informações

- [QUICK_START.md](QUICK_START.md) - Guia completo de início
- [INTERFACES_GUIDE.md](INTERFACES_GUIDE.md) - Guia detalhado
- [README.md](README.md) - Documentação principal
