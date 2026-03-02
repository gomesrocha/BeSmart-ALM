# Phase 7: Document Selection for Requirements Generation

## ✅ Completed

### 1. Backend Fixes
- ✅ Corrigido erro de `Annotated` com `Depends` duplicado
- ✅ Reorganizada ordem de parâmetros (dependências antes de Form params)
- ✅ Backend agora inicia sem erros

### 2. Frontend - Document Selection Component
- ✅ **Selection Mode**: Prop `selectionMode` para ativar modo de seleção
- ✅ **Callback**: `onSelectionChange` para notificar mudanças na seleção
- ✅ **Checkboxes**: Checkboxes em cada documento indexado
- ✅ **Select All/Clear**: Botões para selecionar todos ou limpar seleção
- ✅ **Visual Feedback**: 
  - Contador de documentos selecionados
  - Indicador de documentos não indexados
  - Desabilita seleção de documentos não indexados
- ✅ **Conditional UI**: 
  - Esconde botões de upload/delete em modo seleção
  - Mostra apenas documentos relevantes

### 3. Features Implementadas

#### Selection State Management
```typescript
const [selectedDocuments, setSelectedDocuments] = useState<Set<string>>(new Set())
```

#### Selection Functions
- `toggleDocumentSelection(id)`: Toggle individual document
- `selectAll()`: Seleciona todos os documentos indexados
- `clearSelection()`: Limpa toda a seleção

#### Props Interface
```typescript
interface ProjectDocumentsProps {
  projectId: string
  selectionMode?: boolean  // Ativa modo de seleção
  onSelectionChange?: (selectedIds: string[]) => void  // Callback
}
```

## 🎨 UI Changes

### Normal Mode
- Botões: "Upload File", "Add URL"
- Cards com botão de deletar
- Descrição: "Manage documents..."

### Selection Mode
- Botões: "Select All", "Clear"
- Checkboxes nos cards
- Sem botão de deletar
- Contador: "X selected"
- Descrição: "Select documents to use..."
- Warning para documentos não indexados

## 🔄 Next Integration Steps

### Fase 8: Integrate with Requirements Generation
1. **Update ProjectDetail Page**:
   - Add "Generate from Documents" button
   - Show document selection modal
   - Pass selected document IDs to generation endpoint

2. **Backend Endpoint Enhancement**:
   - Add `document_ids` parameter to `/requirements/generate`
   - Load selected documents from database
   - Extract content from selected documents only
   - Use RAG with selected documents

3. **Workflow**:
   ```
   User clicks "Generate Requirements"
   → Modal opens with ProjectDocuments in selection mode
   → User selects documents
   → User clicks "Generate"
   → Backend uses only selected documents
   → Requirements generated
   ```

## 📝 Example Usage

```typescript
// In a modal or page
<ProjectDocuments
  projectId={projectId}
  selectionMode={true}
  onSelectionChange={(selectedIds) => {
    console.log('Selected documents:', selectedIds)
    setSelectedDocumentIds(selectedIds)
  }}
/>

// Then use selectedDocumentIds in generation request
await api.post('/requirements/generate-from-documents', {
  project_id: projectId,
  document_ids: selectedDocumentIds,
  additional_context: context
})
```

## 🚀 Testing

### 1. Test Selection Mode
```bash
# Start backend
cd services
uvicorn api_gateway.main:app --reload --port 8086

# Start frontend
cd frontend
npm run dev
```

### 2. Test in Browser
1. Login
2. Go to project
3. Click "Documents"
4. Upload some documents
5. Wait for indexing
6. Test selection:
   - Click checkboxes
   - Click "Select All"
   - Click "Clear"
   - Try selecting non-indexed (should be disabled)

## 🎯 Benefits

1. **User Control**: Users choose which documents to use
2. **Performance**: Only process selected documents
3. **Relevance**: Better requirements from relevant documents
4. **Flexibility**: Mix different document types
5. **Transparency**: Clear what's being used

## ✨ What's Next

### Immediate Next Steps:
1. Create modal in ProjectDetail for document selection
2. Add "Generate from Selected Documents" button
3. Update backend endpoint to accept document_ids
4. Implement document loading and RAG with selection
5. Show preview of selected documents before generation

### Future Enhancements:
- Document preview before selection
- Save document selections as "sets"
- Recommend documents based on project type
- Show document relevance scores
- Bulk document operations
- Document tagging for easier selection

## 🐛 Bug Fixes Applied

### Backend Errors Fixed:
```python
# ❌ Before (Error)
async def upload_document(
    file: UploadFile = File(...),
    session: Annotated[AsyncSession, Depends(get_session)] = Depends(get_session),
)

# ✅ After (Fixed)
async def upload_document(
    session: Annotated[AsyncSession, Depends(get_session)],
    file: UploadFile = File(...),
)
```

**Issue**: Cannot use `Annotated[..., Depends(...)]` AND `= Depends(...)` together
**Solution**: Remove default value, keep only `Annotated`

**Issue**: Parameters without defaults after parameters with defaults
**Solution**: Move dependency parameters before Form/File parameters

## 📊 Current Status

- ✅ Backend: Working, no errors
- ✅ Frontend: Selection component ready
- ✅ UI: Polished and intuitive
- ⏳ Integration: Ready for next phase
- ⏳ Backend endpoint: Needs document_ids support

## 🎉 Summary

Phase 7 is complete! The document selection UI is ready and working. Users can now:
- View all project documents
- Select specific documents for generation
- See which documents are indexed
- Get visual feedback on selection

Next phase will integrate this with the requirements generation workflow! 🚀
