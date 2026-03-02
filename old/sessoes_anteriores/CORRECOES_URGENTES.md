# 🔧 Correções Urgentes

**Data**: 23/02/2026  
**Status**: 🔄 **EM ANDAMENTO**

---

## 🐛 Problemas Identificados

### 1. ❌ Erro ao Gerar Arquitetura
**Erro**: `invalid input value for enum documentcategory: "ARCHITECTURE"`

**Causa**: O enum no PostgreSQL não tem o valor 'architecture'

**Análise**:
- Migração foi executada com sucesso
- Enum values foram adicionados: 'generated', 'rag_source', 'architecture'
- Mas PostgreSQL não está reconhecendo

**Solução**:
1. Verificar se enum foi realmente adicionado ao banco
2. Pode precisar recriar o enum ou usar ALTER TYPE
3. Alternativa: Usar valor existente temporariamente

### 2. ❌ Documento de Especificação Não Abre
**Erro**: "Failed to load document"

**Causa**: Investigando...

**Logs Adicionados**:
- Console.log em cada etapa do carregamento
- Verificação de documento encontrado
- Verificação de conteúdo carregado

---

## 🔧 Correções Aplicadas

### 1. Logs de Debug no DocumentViewer
**Arquivo**: `frontend/src/pages/DocumentViewer.tsx`

**Logs Adicionados**:
```typescript
console.log('📄 Loading document:', { projectId, documentId })
console.log('📋 All documents:', docResponse.data)
console.log('🔍 Found document:', doc)
console.log('📥 Loading content for generated document...')
console.log('✅ Content loaded:', contentResponse.data)
```

### 2. Migração Re-executada
**Script**: `scripts/migrate_add_document_fields.py`

**Resultado**: ✅ Todas as 8 migrações completadas

---

## 🧪 Como Investigar

### 1. Verificar Enum no Banco (SQL)

```sql
-- Ver valores do enum
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = (
  SELECT oid 
  FROM pg_type 
  WHERE typname = 'documentcategory'
);
```

**Valores Esperados**:
- requirements
- specification
- architecture ← Deve estar aqui!
- design
- technical
- business
- generated
- rag_source
- other

### 2. Testar Documento de Especificação

1. Gerar especificação
2. Clicar "View Document"
3. Abrir console (F12)
4. Ver logs:
   ```
   📄 Loading document: { projectId: "...", documentId: "..." }
   📋 All documents: [...]
   🔍 Found document: {...}
   📥 Loading content...
   ✅ Content loaded: {...}
   ```

5. Se erro, ver qual etapa falhou

---

## 🔨 Soluções Possíveis

### Para Erro de Enum

**Opção 1: Verificar e Adicionar Manualmente**
```sql
-- Adicionar valor se não existir
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'architecture' 
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'documentcategory')
    ) THEN
        ALTER TYPE documentcategory ADD VALUE 'architecture';
    END IF;
END$$;
```

**Opção 2: Usar Valor Existente Temporariamente**
```python
# Em specification/router.py
category=DocumentCategory.TECHNICAL,  # Temporário
```

**Opção 3: Recriar Enum (Mais drástico)**
```sql
-- Backup, drop, recreate
-- Não recomendado se há dados
```

### Para Documento Não Abrindo

**Verificações**:
1. Documento existe na lista?
2. `is_generated` está true?
3. Endpoint `/content` funciona?
4. Conteúdo está salvo no banco?

**Query SQL**:
```sql
SELECT id, name, category, is_generated, 
       LENGTH(content) as content_length
FROM project_document
WHERE is_generated = true
ORDER BY created_at DESC
LIMIT 5;
```

---

## 🚀 Próximos Passos

### Imediato
1. ✅ Logs adicionados no DocumentViewer
2. ⏳ Testar e ver logs
3. ⏳ Verificar enum no banco
4. ⏳ Corrigir enum se necessário
5. ⏳ Testar geração de arquitetura

### Depois
- Continuar com Kanban Board
- Outras melhorias da Sprint 3

---

## 📝 Comandos Úteis

### Verificar Banco
```bash
# Conectar ao PostgreSQL
psql -U postgres -d bsmart_alm

# Ver enums
\dT+ documentcategory

# Ver documentos
SELECT id, name, category, is_generated 
FROM project_document 
ORDER BY created_at DESC 
LIMIT 10;
```

### Reiniciar Backend
```bash
# Parar (Ctrl+C)
# Reiniciar
cd services
uvicorn api_gateway.main:app --reload --port 8086
```

### Ver Logs
```bash
# Backend logs no terminal
# Frontend logs no console do browser (F12)
```

---

**Status**: 🔄 **INVESTIGANDO**  
**Prioridade**: 🔴 **ALTA**  
**Próximo**: Verificar logs e corrigir enum

🔧 **Trabalhando nisso!**
