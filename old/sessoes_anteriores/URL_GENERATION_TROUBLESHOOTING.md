# 🔧 Troubleshooting - Geração de Requisitos via URL

## 📋 Melhorias Implementadas

Adicionamos logging detalhado e melhor tratamento de erros para facilitar o debug de problemas na geração de requisitos via URL.

---

## 🔍 Como Verificar Logs

### 1. Logs do Backend

Os logs agora mostram cada etapa do processo:

```bash
# Ver logs em tempo real
cd services
uvicorn api_gateway.main:app --reload --log-level info
```

**Logs Esperados**:
```
INFO: Starting URL requirements generation for project xxx, URL: https://...
INFO: Project whitelist: []
INFO: Starting to scrape URL: https://...
INFO: Fetching URL: https://...
INFO: Successfully fetched URL. Status: 200, Content length: 12345
INFO: Extracting text from HTML (length: 12345)
INFO: Extracted text length: 8000 characters
INFO: Successfully scraped URL. Final text length: 8000
INFO: Chunking extracted text
INFO: Created 16 chunks from extracted text
INFO: Finding most relevant chunks using embeddings
INFO: Search query: requirements specifications features...
INFO: Found 5 relevant chunks
INFO: Combined context length: 2500 characters
INFO: Generating requirements with Ollama
INFO: Prompt length: 3000 characters
INFO: Received response from Ollama, length: 1500 characters
INFO: Extracted JSON length: 1400 characters
INFO: Successfully parsed JSON with 7 requirements
INFO: Successfully generated 7 requirements from URL
```

---

## ❌ Problemas Comuns e Soluções

### 1. Ollama Não Está Rodando

**Erro**:
```
Failed to generate requirements from URL: Connection refused
```

**Solução**:
```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Se não estiver, iniciar Ollama
ollama serve

# Em outro terminal, verificar modelo
ollama list
ollama pull llama3.2
```

### 2. URL Bloqueada por CORS/Firewall

**Erro**:
```
Failed to connect to URL: Connection timeout
```

**Soluções**:
- Verificar se a URL é acessível no navegador
- Tentar com outra URL
- Verificar firewall/proxy
- Usar URL alternativa (ex: GitHub Pages ao invés de site privado)

### 3. Página Requer JavaScript

**Erro**:
```
Extracted text is too short (50 characters). The page might be empty or require JavaScript.
```

**Explicação**: O scraper não executa JavaScript, apenas lê HTML estático.

**Soluções**:
- Usar URL de documentação estática (ex: GitHub Pages, ReadTheDocs)
- Procurar versão HTML da página
- Fazer upload do documento ao invés de usar URL

### 4. Conteúdo Muito Grande

**Erro**:
```
Request timeout after 30 seconds
```

**Solução**:
- Usar URL de página específica ao invés de site inteiro
- Aumentar timeout no código (se necessário)
- Fazer upload do documento ao invés de usar URL

### 5. Whitelist Bloqueando URL

**Erro**:
```
URL not in project whitelist. Allowed domains: example.com
```

**Solução**:
1. Editar projeto
2. Adicionar domínio à whitelist
3. Ou deixar whitelist vazia para permitir qualquer URL

### 6. Ollama Não Retorna JSON

**Erro**:
```
No JSON found in AI response. The AI might not be responding correctly.
```

**Soluções**:
```bash
# Verificar modelo Ollama
ollama list

# Testar modelo manualmente
ollama run llama3.2 "Generate a JSON with requirements"

# Se não funcionar, reinstalar modelo
ollama rm llama3.2
ollama pull llama3.2
```

### 7. Página Vazia ou Sem Conteúdo

**Erro**:
```
Extracted text is too short or empty
```

**Verificações**:
1. Abrir URL no navegador
2. Ver se tem conteúdo visível
3. Ver se não é página de login
4. Ver se não requer autenticação

---

## 🧪 Como Testar

### Teste 1: URL Simples

```bash
# URL de teste que deve funcionar
https://example.com
```

1. Criar projeto
2. Ir para "Generate Requirements"
3. Clicar em "URL"
4. Colar URL
5. Clicar "Fetch & Generate"
6. Ver logs no terminal do backend

### Teste 2: GitHub Pages

```bash
# Documentação estática
https://fga-eps-mds.github.io/2018.2-Integra-Vendas/docs/doc-visao
```

1. Usar URL acima
2. Adicionar contexto: "E-commerce platform"
3. Gerar requisitos
4. Verificar logs

### Teste 3: Com Whitelist

1. Editar projeto
2. Adicionar "github.io" à whitelist
3. Tentar URL do GitHub
4. Deve funcionar

5. Tentar URL de outro domínio
6. Deve bloquear

---

## 📊 Verificar Cada Etapa

### 1. Scraping

```python
# Testar scraping isoladamente
from services.requirements.web_scraper import WebScraper
import asyncio

async def test():
    scraper = WebScraper()
    text = await scraper.scrape_url("https://example.com")
    print(f"Extracted {len(text)} characters")
    print(text[:500])

asyncio.run(test())
```

### 2. Embeddings

```python
# Testar embeddings
from services.requirements.embeddings import EmbeddingsClient
import asyncio

async def test():
    client = EmbeddingsClient()
    chunks = ["chunk 1", "chunk 2", "chunk 3"]
    results = await client.find_most_relevant("requirements", chunks, top_k=2)
    print(results)

asyncio.run(test())
```

### 3. Ollama

```bash
# Testar Ollama diretamente
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Generate requirements in JSON format",
  "stream": false
}'
```

---

## 🔧 Configurações Avançadas

### Aumentar Timeout

Editar `services/requirements/web_scraper.py`:

```python
class WebScraper:
    def __init__(self, timeout: int = 60):  # Aumentar de 30 para 60
        self.timeout = timeout
```

### Melhorar Extração de Texto

Editar `services/requirements/web_scraper.py`:

```python
# Adicionar mais tags para remover
for script in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "form"]):
    script.decompose()
```

### Ajustar Chunking

Editar chamada em `router.py`:

```python
chunks = processor.chunk_text(
    extracted_text, 
    chunk_size=1024,  # Aumentar de 512
    overlap=100       # Aumentar de 50
)
```

---

## 📝 Checklist de Debug

Quando algo não funcionar, verificar na ordem:

- [ ] Ollama está rodando? (`curl http://localhost:11434/api/tags`)
- [ ] Modelo está instalado? (`ollama list`)
- [ ] URL é acessível? (abrir no navegador)
- [ ] URL tem conteúdo? (não é página vazia)
- [ ] URL não requer JavaScript? (ver source HTML)
- [ ] Whitelist permite URL? (verificar configuração)
- [ ] Backend está rodando? (ver logs)
- [ ] Logs mostram erro específico? (ler mensagem)

---

## 💡 Dicas

### URLs que Funcionam Bem
- ✅ GitHub Pages
- ✅ ReadTheDocs
- ✅ Sites de documentação estática
- ✅ Páginas HTML simples

### URLs que Podem Ter Problemas
- ❌ SPAs (React, Vue, Angular)
- ❌ Sites que requerem login
- ❌ Sites com muito JavaScript
- ❌ Sites com CAPTCHA
- ❌ Sites muito grandes/lentos

### Alternativas
Se URL não funcionar:
1. Fazer download da página (Save As HTML)
2. Fazer upload do arquivo
3. Copiar texto e colar no modo "Text"

---

## 🎯 Exemplo de Uso Correto

```
1. Projeto: "E-commerce Platform"

2. URL: https://github.com/user/repo/blob/main/docs/requirements.md
   (Usar raw URL: https://raw.githubusercontent.com/user/repo/main/docs/requirements.md)

3. Contexto Adicional: "Focus on payment and checkout features"

4. Resultado: 7-10 requisitos gerados baseados no documento
```

---

## 📞 Suporte

Se o problema persistir após verificar tudo:

1. Copiar logs completos do backend
2. Copiar URL que está tentando usar
3. Copiar mensagem de erro exata
4. Verificar se Ollama responde manualmente

---

**Com logging detalhado, fica muito mais fácil identificar onde está o problema!** 🔍
