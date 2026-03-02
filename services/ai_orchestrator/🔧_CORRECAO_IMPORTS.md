# 🔧 Correção de Imports - AI Orchestrator

## Problema Identificado

```
ImportError: attempted relative import beyond top-level package
```

## Causa

Os scripts `start_web.py` e `start_cli.py` estavam importando módulos diretamente, causando problemas com imports relativos.

## Solução Aplicada

### 1. Atualização dos Scripts de Inicialização

**start_web.py:**
- Mudou de `from web_ui import app` para `uvicorn.run("web_ui:app", ...)`
- Isso permite que o uvicorn carregue o módulo corretamente

**start_cli.py:**
- Importa o `main` apenas dentro do `if __name__ == '__main__'`
- Garante que o path está configurado antes do import

### 2. Criação do setup.sh

Script automatizado que:
- Verifica se `uv` está instalado
- Cria o virtual environment
- Instala todas as dependências
- Fornece instruções claras

### 3. Documentação Atualizada

- **TROUBLESHOOTING.md**: Guia completo de problemas comuns
- **QUICK_START.md**: Instruções simplificadas
- **GUIA_TESTES.md**: Atualizado com setup correto

## Como Usar Agora

```bash
# 1. Setup (primeira vez)
cd services/ai_orchestrator
./setup.sh

# 2. Ativar ambiente
source .venv/bin/activate

# 3. Iniciar
python start_web.py  # Web UI
# ou
python start_cli.py  # CLI
```

## Arquivos Modificados

1. ✅ `start_web.py` - Corrigido import
2. ✅ `start_cli.py` - Corrigido import
3. ✅ `setup.sh` - Novo script de setup
4. ✅ `TROUBLESHOOTING.md` - Novo guia
5. ✅ `QUICK_START.md` - Atualizado
6. ✅ `GUIA_TESTES.md` - Atualizado

## Teste

```bash
# Limpar ambiente anterior (se existir)
rm -rf .venv

# Setup completo
./setup.sh

# Ativar
source .venv/bin/activate

# Testar Web UI
python start_web.py
# Abrir http://localhost:8080

# Testar CLI (em outro terminal)
source .venv/bin/activate
python start_cli.py
```

## Status

✅ Problema resolvido
✅ Scripts funcionando
✅ Documentação atualizada
✅ Setup automatizado criado
