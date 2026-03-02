# Plano de Correção Completo - Permissões e Roles

## Problemas Identificados

### 1. ✅ RESOLVIDO: Botão criar projeto sumiu para superadmin
- **Causa**: Código verificava `is_super_admin` mas modelo tem `is_superuser`
- **Status**: Corrigido

### 2. 🔴 CRÍTICO: Não consegue atribuir roles para superadmin (gomesrocha)
- **Sintoma**: Ao selecionar gomesrocha na tela User Roles e clicar em "+ Assign Role", não funciona
- **Causa Provável**: Backend ou frontend bloqueando atribuição de roles para superadmins

### 3. 🔴 CRÍTICO: Tenant Admin (acme) não vê menu "User Roles"
- **Sintoma**: Usuário acme (admin do tenant ACME) não tem acesso ao menu User Roles
- **Causa Provável**: Permissões do Sidebar não incluem tenant admins

### 4. 🔴 CRÍTICO: Tenant Admin não consegue gerenciar permissões no próprio tenant
- **Sintoma**: Admin do tenant não consegue dar permissões para usuários do seu tenant
- **Causa Provável**: Falta de permissões adequadas para tenant admins

### 5. 🟡 UX: Falta feedback visual nas ações (toast notifications)
- **Sintoma**: Ao criar projeto, atribuir role, etc., não aparece mensagem de sucesso/erro
- **Exemplo**: Criou projeto como gomesrocha, não deu mensagem, só viu depois que saiu
- **Causa**: Sistema não tem toast notifications implementadas
- **Impacto**: Usuário não sabe se ação foi bem-sucedida

## Hierarquia de Permissões Esperada

```
SUPERADMIN (gomesrocha)
├── Pode fazer TUDO em TODOS os tenants
├── Pode criar/editar/deletar tenants
├── Pode gerenciar usuários de qualquer tenant
├── Pode atribuir qualquer role para qualquer usuário
└── Pode ver todas as telas de administração

TENANT ADMIN (acme no tenant ACME)
├── Pode fazer TUDO no SEU tenant
├── Pode gerenciar usuários do seu tenant
├── Pode atribuir roles para usuários do seu tenant
├── Pode criar projetos no seu tenant
└── Pode ver telas de administração do tenant (Users, User Roles)

DEVELOPER (usuário comum)
├── Pode ver projetos do seu tenant
├── Pode criar/editar work items
└── Acesso limitado baseado em roles
```

## Plano de Correção

### Fase 1: Diagnóstico Completo
**Objetivo**: Entender exatamente o que está quebrado

#### Task 1.1: Criar script de diagnóstico
- Verificar permissões de gomesrocha (superadmin)
- Verificar permissões de acme (tenant admin)
- Verificar roles disponíveis em cada tenant
- Verificar endpoint `/auth/permissions` para cada usuário

#### Task 1.2: Testar atribuição de roles
- Tentar atribuir role via API para superadmin
- Tentar atribuir role via API para tenant admin
- Capturar erros e logs

### Fase 2: Correção Backend

#### Task 2.1: Corrigir endpoint de atribuição de roles
**Arquivo**: `services/identity/role_router.py`
- Permitir que superadmins atribuam roles para qualquer usuário
- Permitir que tenant admins atribuam roles para usuários do seu tenant
- Adicionar validações corretas

#### Task 2.2: Corrigir permissões do Tenant Admin
**Arquivo**: `services/identity/permission_service.py`
- Garantir que tenant admins tenham permissões de gerenciamento no seu tenant
- Adicionar permissões: `user:role:assign`, `user:role:remove`, `user:role:read`

#### Task 2.3: Criar/Atualizar role "Tenant Admin"
**Arquivo**: Script de seed
- Garantir que role "Tenant Admin" existe em cada tenant
- Incluir todas as permissões necessárias
- Atribuir automaticamente ao primeiro usuário do tenant

### Fase 3: Correção Frontend

#### Task 3.1: Corrigir Sidebar para Tenant Admins
**Arquivo**: `frontend/src/components/Sidebar.tsx`
- Adicionar lógica para mostrar "User Roles" para tenant admins
- Verificar permissão `user:role:read` ou role "Tenant Admin"

#### Task 3.2: Corrigir página User Roles
**Arquivo**: `frontend/src/pages/UserRoles.tsx`
- Permitir atribuição de roles para superadmins
- Filtrar roles disponíveis baseado no tipo de usuário
- Melhorar mensagens de erro

#### Task 3.3: Atualizar PermissionContext
**Arquivo**: `frontend/src/contexts/PermissionContext.tsx`
- Adicionar helper `isTenantAdmin()`
- Garantir que tenant admins tenham permissões corretas

### Fase 4: Implementar Toast Notifications

#### Task 4.1: Criar sistema de notificações
**Arquivo**: `frontend/src/contexts/ToastContext.tsx` (novo)
- Criar contexto de toast notifications
- Suportar tipos: success, error, warning, info
- Auto-dismiss após 3-5 segundos
- Posição: top-right

#### Task 4.2: Criar componente Toast
**Arquivo**: `frontend/src/components/Toast.tsx` (novo)
- Componente visual de notificação
- Animações de entrada/saída
- Ícones por tipo
- Botão de fechar manual

#### Task 4.3: Adicionar toasts em todas as ações
**Arquivos**: Múltiplos
- `Projects.tsx`: "Project created successfully", "Failed to create project"
- `UserRoles.tsx`: "Role assigned successfully", "Failed to assign role"
- `Tenants.tsx`: "Tenant created successfully", etc.
- `Users.tsx`: "User created successfully", etc.
- Todas as páginas com formulários/ações

### Fase 5: Testes e Validação

#### Task 5.1: Testar fluxo completo do Superadmin
- Login como gomesrocha
- Atribuir role para outro usuário
- Verificar todas as telas de admin

#### Task 5.2: Testar fluxo completo do Tenant Admin
- Login como acme
- Verificar menu User Roles aparece
- Atribuir role para usuário do tenant
- Criar projeto

#### Task 5.3: Testar isolamento entre tenants
- Verificar que tenant admin não vê usuários de outros tenants
- Verificar que tenant admin não pode atribuir roles em outros tenants

#### Task 5.4: Testar toast notifications
- Criar projeto e verificar mensagem de sucesso
- Tentar criar com erro e verificar mensagem de erro
- Atribuir role e verificar feedback
- Verificar auto-dismiss funciona
- Verificar múltiplas notificações simultâneas

## Ordem de Execução

1. **AGORA**: Task 1.1 - Criar script de diagnóstico
2. **DEPOIS**: Task 2.1, 2.2, 2.3 - Correções backend
3. **DEPOIS**: Task 3.1, 3.2, 3.3 - Correções frontend
4. **DEPOIS**: Task 4.1, 4.2, 4.3 - Toast notifications
5. **FINAL**: Task 5.1, 5.2, 5.3, 5.4 - Testes

## Arquivos que Serão Modificados

### Backend
- `services/identity/role_router.py` - Endpoint de atribuição de roles
- `services/identity/permission_service.py` - Lógica de permissões
- `scripts/create_default_roles.py` - Seed de roles padrão
- Novo: `scripts/fix_tenant_admin_permissions.py` - Script de correção

### Frontend
- `frontend/src/components/Sidebar.tsx` - Menu lateral
- `frontend/src/pages/UserRoles.tsx` - Página de gerenciamento
- `frontend/src/contexts/PermissionContext.tsx` - Contexto de permissões
- Novo: `frontend/src/contexts/ToastContext.tsx` - Sistema de notificações
- Novo: `frontend/src/components/Toast.tsx` - Componente de toast
- `frontend/src/pages/Projects.tsx` - Adicionar toasts
- `frontend/src/pages/Tenants.tsx` - Adicionar toasts
- `frontend/src/pages/Users.tsx` - Adicionar toasts

## Critérios de Sucesso

✅ Superadmin pode atribuir qualquer role para qualquer usuário
✅ Tenant Admin vê menu "User Roles"
✅ Tenant Admin pode atribuir roles para usuários do seu tenant
✅ Tenant Admin NÃO pode atribuir roles em outros tenants
✅ Todas as permissões funcionam corretamente
✅ Isolamento entre tenants mantido
✅ Toast notifications aparecem em todas as ações
✅ Usuário recebe feedback claro de sucesso/erro

## Próximo Passo

Começar com Task 1.1 - Criar script de diagnóstico completo para entender exatamente o que está quebrado.
