# Phase 6: Project Document Management & RAG

## ✅ Completed

### 1. Backend - Document Models
- **`ProjectDocument` Model**: Armazena documentos do projeto
  - Suporte para PDF, DOCX, TXT e URLs
  - Categorização (requirements, specification, design, technical, business, other)
  - Metadados RAG (is_indexed, chunk_count, indexed_at)
  - Hash de conteúdo para evitar duplicatas
  - Informações de upload (usuário, data, tamanho)

### 2. Backend - Document Endpoints
- **GET `/projects/{id}/documents`**: Listar documentos do projeto
  - Filtro por categoria
  - Ordenação por data de upload
- **POST `/projects/{id}/documents/upload`**: Upload de arquivo
  - Suporte para PDF, DOCX, TXT
  - Processamento automático e indexação
  - Chunking para RAG
- **POST `/projects/{id}/documents/url`**: Adicionar URL
  - Web scraping automático
  - Indexação do conteúdo
- **PATCH `/projects/{id}/documents/{doc_id}`**: Atualizar metadados
- **DELETE `/projects/{id}/documents/{doc_id}`**: Deletar documento

### 3. Frontend - Document Management UI
- **Componente `ProjectDocuments`**:
  - Listagem de documentos com filtros por categoria
  - Upload de arquivos (drag & drop ready)
  - Adicionar URLs
  - Visualização de metadados (tamanho, chunks, data)
  - Indicador de indexação
  - Deletar documentos
  
- **Página `ProjectDocumentsPage`**:
  - Página dedicada para gerenciar documentos
  - Navegação integrada com projeto

- **Integração com ProjectDetail**:
  - Botão "Documents" no header do projeto
  - Link direto para página de documentos

### 4. Features Implementadas
- ✅ Upload de múltiplos tipos de arquivo
- ✅ Adicionar URLs com scraping automático
- ✅ Categorização de documentos
- ✅ Indexação automática para RAG
- ✅ Chunking de conteúdo
- ✅ Filtros por categoria
- ✅ Metadados completos
- ✅ Deleção de documentos
- ✅ UI responsiva e intuitiva

## 📊 Categorias de Documentos

1. **Requirements**: Documentos de requisitos
2. **Specification**: Especificações técnicas
3. **Design**: Documentos de design
4. **Technical**: Documentação técnica
5. **Business**: Documentos de negócio
6. **Other**: Outros documentos

## 🎨 UI Features

### Document Card
- Ícone por tipo (arquivo/URL)
- Nome e descrição
- Badge de categoria com cores
- Tamanho do arquivo
- Status de indexação
- Número de chunks
- Data de upload
- Botão de deletar

### Modals
- **Upload Modal**: Formulário para upload de arquivo
- **URL Modal**: Formulário para adicionar URL
- Validação de campos
- Loading states

### Filtros
- Botões de categoria (all, requirements, specification, etc.)
- Filtro visual ativo
- Atualização automática da lista

## 🔄 Próximos Passos

### Fase 7: Seleção de Documentos para Geração
1. **Checkbox de seleção** em cada documento
2. **Botão "Generate Requirements"** com documentos selecionados
3. **Endpoint melhorado** que aceita lista de document_ids
4. **RAG aprimorado** usando apenas documentos selecionados
5. **Preview de documentos** selecionados antes de gerar

### Melhorias Futuras
- Preview de documentos (PDF viewer, markdown renderer)
- Download de documentos
- Versionamento de documentos
- Compartilhamento de documentos
- Comentários em documentos
- Tags personalizadas
- Busca full-text
- Drag & drop para upload
- Bulk operations (deletar múltiplos)
- Estatísticas de uso

## 🚀 Como Testar

### 1. Iniciar Backend
```bash
cd services
uvicorn api_gateway.main:app --reload --port 8086
```

### 2. Iniciar Frontend
```bash
cd frontend
npm run dev
```

### 3. Testar Document Management
1. Login: admin@example.com / admin123
2. Criar ou abrir um projeto
3. Clicar em "Documents" no header
4. **Upload de arquivo**:
   - Clicar em "Upload File"
   - Selecionar PDF, DOCX ou TXT
   - Escolher categoria
   - Adicionar descrição (opcional)
   - Upload
5. **Adicionar URL**:
   - Clicar em "Add URL"
   - Inserir URL
   - Dar um nome
   - Escolher categoria
   - Adicionar
6. **Filtrar por categoria**:
   - Clicar nos botões de categoria
   - Ver lista filtrada
7. **Deletar documento**:
   - Clicar no ícone de lixeira
   - Confirmar

## 📝 API Endpoints

```
GET    /api/v1/projects/{id}/documents              - Listar documentos
POST   /api/v1/projects/{id}/documents/upload       - Upload arquivo
POST   /api/v1/projects/{id}/documents/url          - Adicionar URL
PATCH  /api/v1/projects/{id}/documents/{doc_id}     - Atualizar
DELETE /api/v1/projects/{id}/documents/{doc_id}     - Deletar
```

## 🗄️ Banco de Dados

### Tabela: project_document
```sql
- id: UUID (PK)
- tenant_id: UUID (FK)
- project_id: UUID (FK)
- name: VARCHAR(500)
- type: ENUM (pdf, docx, txt, url, other)
- category: ENUM (requirements, specification, design, technical, business, other)
- url: VARCHAR(2000) (nullable)
- file_path: VARCHAR(1000) (nullable)
- file_size: INTEGER (nullable)
- content_hash: VARCHAR(64) (nullable)
- description: TEXT (nullable)
- uploaded_by: UUID (FK)
- uploaded_at: TIMESTAMP
- is_indexed: BOOLEAN
- chunk_count: INTEGER
- indexed_at: TIMESTAMP (nullable)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

## 🎯 Benefícios

1. **Organização**: Todos os documentos do projeto em um só lugar
2. **RAG Preparado**: Documentos automaticamente indexados
3. **Flexibilidade**: Suporte para arquivos e URLs
4. **Categorização**: Fácil encontrar documentos por tipo
5. **Metadados**: Informações completas sobre cada documento
6. **Integração**: Pronto para usar na geração de requisitos

## ✨ Próxima Implementação

Na **Fase 7**, vamos implementar:
- Seleção de documentos específicos para geração
- Geração de requisitos usando documentos selecionados
- Preview de documentos antes de gerar
- Workflow completo: Upload → Selecionar → Gerar

O sistema agora tem uma base sólida para gerenciamento de documentos e está pronto para integração completa com a geração de requisitos! 🚀
