# 🎯 Correções Restantes - Guia Rápido

## ✅ Já Corrigido (2/13)

1. ✅ **Edição de Projeto** - FUNCIONANDO
2. ✅ **Especificação Abre** - FUNCIONANDO

## 🔄 Próximas Correções (11 restantes)

### 🔴 P0 - Crítico (4 bugs)

#### 3. Progress Step Não Fica Verde
**Arquivo**: `frontend/src/pages/ProjectDetail.tsx`
**Problema**: Lógica de verificação incorreta
**Solução**: Verificar categoria correta dos documentos

#### 4. Work Item - Mudança de Status
**Arquivo**: `frontend/src/pages/WorkItemDetail.tsx`
**Problema**: Não há dropdown de status
**Solução**: Adicionar dropdown + função handleStatusChange

#### 5. Assigned To Não Funciona
**Arquivo**: `frontend/src/pages/WorkItemDetail.tsx`
**Problema**: Dropdown não carrega usuários
**Solução**: Carregar usuários + dropdown + função handleAssigneeChange

#### 6. Submit for Review com Erro
**Arquivo**: `frontend/src/pages/WorkItemDetail.tsx`
**Problema**: Error handling ruim
**Solução**: Melhorar try/catch e mensagens

### 🟡 P1 - Alto (5 bugs)

#### 7. AI Stats Vazio
**Ação**: Executar `uv run python scripts/migrate_ai_stats.py`

#### 8. Documentos Uploaded Não Aparecem
**Arquivo**: `services/project/document_router.py`
**Problema**: Query pode estar filtrando incorretamente
**Solução**: Verificar query de listagem

#### 9. Formatação de Requisitos Ruim
**Arquivo**: `frontend/src/pages/WorkItemDetail.tsx`
**Problema**: CSS e estrutura HTML ruins
**Solução**: Componente RequirementDetails melhorado

#### 10. Kanban Precisa Teste
**Ação**: Testar `/work-items/kanban`

#### 11. Multi-tenant Incompleto
**Ação**: Verificar queries em todos os routers

### 🔵 P2 - Médio (2 bugs)

#### 12. Settings Não Implementado
**Ação**: Criar página Settings

#### 13. Testes Automatizados
**Ação**: Adicionar testes E2E

---

## 🚀 Vou Aplicar Agora

Vou aplicar as correções 3-6 (P0) que são críticas e rápidas.

**Tempo estimado**: 30-40 minutos

**Ordem**:
1. Progress Step (5 min)
2. Mudança de Status (10 min)
3. Assigned To (15 min)
4. Submit for Review (5 min)

Depois você testa e vemos as próximas! 🎯
