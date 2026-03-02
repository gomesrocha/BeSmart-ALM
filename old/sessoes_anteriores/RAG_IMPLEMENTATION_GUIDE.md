# 🚀 RAG Implementation Guide - Document Upload & Semantic Search

## ✨ Nova Funcionalidade: Upload de Documentos com RAG!

Agora você pode fazer upload de documentos (PDF, DOCX, TXT) e a IA vai extrair e analisar o conteúdo usando RAG (Retrieval-Augmented Generation) com embeddings semânticos!

## 🎯 O que foi implementado

### Backend (3 novos arquivos)

1. **`services/requirements/document_processor.py`**
   - Extração de texto de PDF (PyPDF2)
   - Extração de texto de DOCX (python-docx)
   - Extração de texto de TXT
   - Chunking inteligente com overlap

2. **`services/requirements/embeddings.py`**
   - Cliente para gerar embeddings com `nomic-embed-text`
   - Busca semântica com cosine similarity
   - Encontrar chunks mais relevantes

3. **`services/requirements/router.py`** (atualizado)
   - Novo endpoint: `/api/v1/requirements/generate-from-document`
   - Suporte para upload de arquivos
   - RAG pipeline completo

### Frontend (atualizado)

1. **`frontend/src/pages/ProjectDetail.tsx`**
   - Toggle entre texto e upload
   - Interface de upload de documentos
   - Suporte para contexto adicional
   - Feedback visual durante processamento

## 🔧 Instalação de Dependências

```bash
# Instalar bibliotecas Python necessárias
pip install PyPDF2 python-docx numpy

# Ou com UV
uv pip install PyPDF2 python-docx numpy
```

## 🚀 Como Funciona o RAG

### 1. Upload do Documento
```
Usuário faz upload → PDF/DOCX/TXT
```

### 2. Extração de Texto
```
Documento → Extrator → Texto completo
```

### 3. Chunking
```
Texto completo → Chunks de 512 palavras com overlap de 50
```

### 4. Geração de Embeddings
```
Cada chunk → nomic-embed-text → Vector (768 dimensões)
```

### 5. Busca Semântica
```
Query: "requirements specifications features"
→ Embedding da query
→ Cosine similarity com todos os chunks
→ Top 5 chunks mais relevantes
```

### 6. Geração de Requisitos
```
Chunks relevantes → Contexto para LLM
→ llama3.2 gera requisitos
→ Formato estruturado (JSON)
```

## 📝 Como Usar

### Opção 1: Texto (como antes)

1. Ir para Projects
2. Clicar em um projeto
3. Selecionar "Text Description"
4. Descrever o projeto
5. Clicar em "Generate Requirements"

### Opção 2: Upload de Documento (NOVO!)

1. Ir para Projects
2. Clicar em um projeto
3. Selecionar "Upload Document"
4. Escolher arquivo (PDF, DOCX ou TXT)
5. (Opcional) Adicionar contexto adicional
6. Clicar em "Upload & Generate Requirements"
7. Aguardar processamento (30-60 segundos)
8. Revisar requisitos gerados
9. Aprovar e criar work items

## 📄 Formatos Suportados

### PDF
- Extrai texto de todas as páginas
- Suporta PDFs com texto selecionável
- **Não suporta**: PDFs escaneados (sem OCR)

### DOCX
- Extrai texto de todos os parágrafos
- Mantém estrutura básica
- Suporta documentos do Word

### TXT
- Lê arquivos de texto simples
- Suporta UTF-8 e Latin-1
- Ideal para especificações técnicas

## 🎯 Exemplo de Uso

### Documento de Entrada (PDF)
```
Sistema de Biblioteca Online

Funcionalidades:
1. Catálogo de livros com busca avançada
2. Sistema de empréstimo com controle de datas
3. Notificações automáticas de devolução
4. Área administrativa para bibliotecários
5. Relatórios de livros mais emprestados
6. Sistema de reservas

Requisitos Técnicos:
- Interface web responsiva
- Suporte para 1000 usuários simultâneos
- Backup diário automático
- Integração com sistema de pagamento
```

### Saída (Requisitos Gerados)
```json
{
  "requirements": [
    {
      "title": "Advanced Book Search",
      "user_story": "As a library user, I want to search for books by title, author, or category, so that I can quickly find the books I need",
      "acceptance_criteria": [
        "WHEN user enters search term THEN system SHALL display matching books within 2 seconds",
        "IF no books found THEN system SHALL display helpful suggestions",
        "WHERE search results system SHALL support filtering by availability"
      ],
      "type": "requirement",
      "priority": "high"
    },
    ...
  ]
}
```

## 🔍 Como o RAG Melhora a Geração

### Sem RAG (apenas descrição)
- IA gera requisitos genéricos
- Pode perder detalhes específicos
- Limitado ao que você escreve

### Com RAG (documento + embeddings)
- IA analisa documento completo
- Encontra seções mais relevantes
- Mantém detalhes técnicos
- Gera requisitos mais precisos
- Usa terminologia do documento

## 🎨 Fluxo Completo

```
┌─────────────────┐
│  Upload PDF     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract Text    │
│ (PyPDF2)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Chunk Text      │
│ (512 words)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate        │
│ Embeddings      │
│ (nomic-embed)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Semantic Search │
│ (Top 5 chunks)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Reqs   │
│ (llama3.2)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Structured JSON │
│ Requirements    │
└─────────────────┘
```

## 🐛 Troubleshooting

### Erro: "PyPDF2 is required"
```bash
pip install PyPDF2
# ou
uv pip install PyPDF2
```

### Erro: "python-docx is required"
```bash
pip install python-docx
# ou
uv pip install python-docx
```

### Erro: "numpy is required"
```bash
pip install numpy
# ou
uv pip install numpy
```

### Erro: "Failed to extract text from PDF"
**Causa**: PDF escaneado (imagem)
**Solução**: Converter PDF para texto primeiro ou usar OCR

### Erro: "No text could be extracted"
**Causa**: Documento vazio ou corrompido
**Solução**: Verificar o documento e tentar novamente

### Upload muito lento
**Causa**: Documento muito grande
**Solução**: 
- Dividir documento em partes menores
- Usar apenas seções relevantes
- Limitar a 50 páginas

## 📊 Performance

### Tempos Estimados

| Operação | Tempo |
|----------|-------|
| Upload (1MB) | 1-2s |
| Extração PDF (10 páginas) | 2-3s |
| Chunking | < 1s |
| Embeddings (50 chunks) | 10-15s |
| Busca Semântica | < 1s |
| Geração LLM | 15-30s |
| **Total** | **30-60s** |

### Otimizações

- Chunks são processados em paralelo
- Embeddings são cacheados (futuro)
- Busca semântica é muito rápida
- LLM usa apenas chunks relevantes

## 🎯 Próximas Melhorias

1. **OCR para PDFs escaneados**
   - Tesseract integration
   - Suporte para imagens

2. **Cache de Embeddings**
   - Armazenar embeddings no banco
   - Evitar reprocessamento

3. **Mais formatos**
   - Markdown (.md)
   - HTML
   - Excel (.xlsx)

4. **Busca Híbrida**
   - Combinar busca semântica + keyword
   - Melhor precisão

5. **Visualização de Chunks**
   - Mostrar quais partes foram usadas
   - Highlight no documento original

## ✅ Checklist de Uso

- [ ] Ollama rodando (porta 11434)
- [ ] Modelo llama3.2:latest instalado
- [ ] Modelo nomic-embed-text:latest instalado
- [ ] Dependências Python instaladas (PyPDF2, python-docx, numpy)
- [ ] Backend reiniciado
- [ ] Frontend rodando

## 🎉 Resultado

Agora você tem um sistema completo de geração de requisitos com:

✅ Upload de documentos
✅ Extração inteligente de texto
✅ Embeddings semânticos
✅ Busca por relevância (RAG)
✅ Geração contextualizada de requisitos
✅ Interface intuitiva

**RAG implementado com sucesso!** 🚀
