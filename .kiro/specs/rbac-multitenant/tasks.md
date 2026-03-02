# Implementation Plan - RBAC e Multi-Tenant

## Overview

Este documento define o plano de implementação incremental para o sistema de RBAC e Multi-Tenant. As tarefas estão organizadas em ordem de execução, priorizando funcionalidades que entregam valor rapidamente e servem de base para as próximas.

---

## Implementation Tasks

- [x] 1. Preparar Banco de Dados e Modelos
  - Criar script SQLModel para novas tabelas
  - Implementar modelos SQLModel
  - Adicionar índices de performance
  - _Requirements: 2, 11_

- [x] 1.1 Criar script para tabela roles
  - Criar script scripts/create_rbac_tables.py
  - Definir modelo Role com SQLModel
  - Incluir índices em name e level
  - _Requirements: 3, 4, 5, 6, 7, 8, 9_

- [x] 1.2 Adicionar tabela user_roles ao script
  - Definir modelo UserRole com SQLModel
  - Adicionar foreign keys e índices
  - Adicionar constraint único
  - _Requirements: 3, 4, 5, 6, 7, 8, 9_

- [x] 1.3 Adicionar tabela audit_logs ao script
  - Definir modelo AuditLog com SQLModel
  - Adicionar índices em tenant_id, created_at, action
  - _Requirements: 12_

- [x] 1.4 Melhorar tabela tenants
  - Adicionar campos: subscription_plan, max_users, max_projects
  - Adicionar campos: logo_url, domain
  - Atualizar modelo Tenant
  - _Requirements: 2_

- [x] 1.5 Atualizar modelo User
  - Adicionar campo is_super_admin
  - Adicionar campos last_login_at, last_login_ip
  - Adicionar relacionamento com user_roles
  - _Requirements: 3_

- [x] 1.6 Criar modelos SQLModel
  - Implementar modelo Role em services/identity/models.py
  - Implementar modelo UserRole em services/identity/models.py
  - Implementar modelo AuditLog em services/identity/models.py
  - _Requirements: 3, 4, 5, 6, 7, 8, 9, 12_

- [x] 1.7 Executar script de criação
  - Rodar python scripts/create_rbac_tables.py
  - Verificar estrutura do banco
  - _Requirements: 2, 3, 11, 12_

- [x] 2. Implementar Serviços Base
  - Criar PermissionService
  - Criar TenantService
  - Criar AuditService
  - _Requirements: 11, 12, 13_

- [x] 2.1 Criar PermissionService
  - Criar arquivo services/identity/permission_service.py
  - Implementar método check_permission()
  - Implementar método get_user_permissions()
  - Implementar cache de permissões
  - _Requirements: 13_

- [x] 2.2 Criar TenantService
  - Criar arquivo services/identity/tenant_service.py
  - Implementar método create_tenant()
  - Implementar método get_tenant()
  - Implementar método update_tenant()
  - _Requirements: 2_

- [x] 2.3 Criar AuditService
  - Criar arquivo services/identity/audit_service.py
  - Implementar método log_action()
  - Implementar método get_audit_logs()
  - _Requirements: 12_

- [x] 2.4 Criar decorators de permissão
  - Criar arquivo services/identity/decorators.py
  - Implementar decorator @require_permission
  - Implementar decorator @require_any_permission
  - Implementar decorator @require_all_permissions
  - _Requirements: 13_

- [x] 3. Criar Roles Padrão e Seed
  - Criar script de seed para roles
  - Definir permissões de cada role
  - Executar seed
  - _Requirements: 3, 4, 5, 6, 7, 8, 9_

- [x] 3.1 Criar script de seed
  - Criar arquivo scripts/seed_roles.py
  - Definir roles: super_admin, company_admin, project_manager
  - Definir roles: po_analyst, architect, developer, qa
  - Definir permissões de cada role
  - _Requirements: 3, 4, 5, 6, 7, 8, 9_

- [x] 3.2 Executar seed de roles
  - Rodar script seed_roles.py
  - Verificar roles criados no banco
  - _Requirements: 3, 4, 5, 6, 7, 8, 9_

- [x] 4. Implementar Endpoints de Gerenciamento
  - Criar rotas para gerenciar tenants
  - Criar rotas para gerenciar roles
  - Criar rotas para atribuir roles
  - _Requirements: 2, 3, 4_

- [x] 4.1 Criar router de tenants
  - Criar arquivo services/identity/tenant_router.py
  - Implementar POST /tenants (criar empresa)
  - Implementar GET /tenants (listar empresas)
  - Implementar PATCH /tenants/{id} (atualizar empresa)
  - Adicionar verificação de permissão (super_admin)
  - _Requirements: 2, 3_

- [x] 4.2 Criar router de roles
  - Criar arquivo services/identity/role_router.py (já existe, atualizar)
  - Implementar GET /roles (listar roles)
  - Implementar POST /users/{user_id}/roles (atribuir role)
  - Implementar DELETE /users/{user_id}/roles/{role_id} (remover role)
  - Adicionar verificação de permissão
  - _Requirements: 4, 5_

- [x] 4.3 Criar endpoint de permissões do usuário
  - Adicionar GET /auth/permissions em token_router.py
  - Retornar lista de permissões do usuário logado
  - _Requirements: 13_

- [x] 5. Atualizar JWT com Tenant e Roles
  - Incluir tenant_id no token
  - Incluir is_super_admin no token
  - Incluir roles no token (opcional)
  - _Requirements: 11, 13_

- [x] 5.1 Atualizar geração de token
  - Modificar services/identity/security.py
  - Incluir tenant_id no payload do JWT
  - Incluir is_super_admin no payload
  - _Requirements: 11, 13_

- [x] 5.2 Atualizar validação de token
  - Modificar get_current_user em dependencies.py
  - Extrair tenant_id do token
  - Extrair is_super_admin do token
  - _Requirements: 11, 13_

- [x] 6. Implementar Middleware de Tenant
  - Criar middleware para injetar tenant_id
  - Adicionar ao API Gateway
  - _Requirements: 11_

- [x] 6.1 Criar TenantMiddleware
  - Criar arquivo services/shared/middleware/tenant_middleware.py
  - Extrair tenant_id do token JWT
  - Injetar no request.state
  - _Requirements: 11_

- [x] 6.2 Registrar middleware no API Gateway
  - Adicionar middleware em services/api_gateway/main.py
  - Testar injeção de tenant_id
  - _Requirements: 11_

- [x] 7. Adicionar Verificação de Permissões nas Rotas Existentes
  - Atualizar rotas de projetos
  - Atualizar rotas de work items
  - Atualizar rotas de documentos
  - _Requirements: 5, 6, 7, 8, 9, 13_

- [x] 7.1 Atualizar rotas de projetos
  - Adicionar @require_permission("project.create") em create_project
  - Adicionar @require_permission("project.update") em update_project
  - Adicionar @require_permission("project.delete") em delete_project
  - Garantir filtro por tenant_id em todas as queries
  - _Requirements: 5, 11, 13_

- [x] 7.2 Atualizar rotas de work items
  - Adicionar @require_permission("workitem.create") em create_work_item
  - Adicionar @require_permission("workitem.update") em update_work_item
  - Adicionar verificação de ownership para developers
  - Garantir filtro por tenant_id
  - _Requirements: 8, 9, 11, 13_

- [x] 7.3 Atualizar rotas de documentos
  - Adicionar @require_permission("document.upload") em upload_document
  - Adicionar @require_permission("requirements.generate") em generate_requirements
  - Adicionar @require_permission("specification.generate") em generate_specification
  - Adicionar @require_permission("architecture.generate") em generate_architecture
  - _Requirements: 6, 7, 13_

- [x] 8. Implementar Auditoria
  - Adicionar log de ações em rotas críticas
  - Criar endpoint para visualizar logs
  - _Requirements: 12_

- [x] 8.1 Adicionar auditoria em rotas críticas
  - Adicionar log em create/update/delete de projetos
  - Adicionar log em create/update/delete de usuários
  - Adicionar log em atribuição de roles
  - Adicionar log em mudanças de status de work items
  - _Requirements: 12_

- [x] 8.2 Criar endpoint de auditoria
  - Adicionar GET /audit-logs em audit_router.py (novo)
  - Filtrar por tenant_id automaticamente
  - Permitir filtros por: usuário, ação, data
  - Adicionar paginação
  - _Requirements: 12_

- [x] 9. Frontend - Context e Hooks
  - Criar PermissionContext
  - Criar usePermissions hook
  - Criar componente Protected
  - _Requirements: 13_

- [x] 9.1 Criar PermissionContext
  - Criar arquivo frontend/src/contexts/PermissionContext.tsx
  - Implementar PermissionProvider
  - Carregar permissões do backend
  - Implementar métodos: hasPermission, hasAnyPermission, hasAllPermissions
  - _Requirements: 13_

- [x] 9.2 Criar usePermissions hook
  - Criar arquivo frontend/src/hooks/usePermissions.ts
  - Exportar hook que usa PermissionContext
  - _Requirements: 13_

- [x] 9.3 Criar componente Protected
  - Criar arquivo frontend/src/components/Protected.tsx
  - Implementar renderização condicional por permissão
  - Suportar fallback quando sem permissão
  - _Requirements: 13_

- [x] 9.4 Adicionar PermissionProvider no App
  - Envolver App com PermissionProvider em App.tsx
  - _Requirements: 13_

- [x] 10. Frontend - Filtro de Projeto em Work Items
  - Adicionar ProjectSelector
  - Implementar filtro por projeto
  - Salvar seleção no localStorage
  - _Requirements: 1_

- [x] 10.1 Criar componente ProjectSelector
  - Criar arquivo frontend/src/components/ProjectSelector.tsx
  - Carregar lista de projetos
  - Implementar dropdown de seleção
  - Salvar seleção no localStorage
  - _Requirements: 1_

- [x] 10.2 Adicionar filtro em WorkItems
  - Adicionar ProjectSelector em frontend/src/pages/WorkItems.tsx
  - Filtrar work items pelo projeto selecionado
  - Restaurar última seleção ao carregar página
  - _Requirements: 1_

- [x] 10.3 Adicionar filtro em WorkItemsKanban
  - Adicionar ProjectSelector em frontend/src/pages/WorkItemsKanban.tsx
  - Filtrar work items do Kanban pelo projeto selecionado
  - Restaurar última seleção ao carregar página
  - Exigir seleção de projeto antes de mostrar Kanban
  - _Requirements: 1, 10_

- [x] 11. Frontend - Telas de Gerenciamento
  - Criar tela de gerenciamento de empresas
  - Criar tela de gerenciamento de usuários e roles
  - Proteger com permissões
  - _Requirements: 2, 3, 4_

- [x] 11.1 Criar tela de empresas (Super Admin)
  - Criar arquivo frontend/src/pages/Tenants.tsx
  - Listar empresas
  - Formulário de criação de empresa
  - Proteger com permissão "tenant.create"
  - _Requirements: 2, 3_

- [x] 11.2 Criar tela de gerenciamento de roles
  - Criar arquivo frontend/src/pages/UserRoles.tsx
  - Listar usuários da empresa
  - Atribuir/remover roles
  - Proteger com permissão "user.role.assign"
  - _Requirements: 4_

- [x] 11.3 Adicionar rotas no App.tsx
  - Adicionar rota /tenants
  - Adicionar rota /user-roles
  - Proteger rotas com PrivateRoute
  - _Requirements: 2, 4_

- [x] 12. Frontend - Atualizar Componentes Existentes
  - Ocultar botões sem permissão
  - Adicionar feedback quando ação negada
  - _Requirements: 13_

- [x] 12.1 Atualizar página de Projects
  - Envolver botão "New Project" com <Protected permission="project.create">
  - Envolver botão "Edit" com <Protected permission="project.update">
  - Envolver botão "Delete" com <Protected permission="project.delete">
  - _Requirements: 5, 13_

- [x] 12.2 Atualizar página de WorkItems
  - Envolver botão "New Work Item" com <Protected permission="workitem.create">
  - Envolver ações de edição com verificação de permissão
  - _Requirements: 8, 13_

- [x] 12.3 Atualizar página de ProjectDetail
  - Envolver "Generate Requirements" com <Protected permission="requirements.generate">
  - Envolver "Generate Specification" com <Protected permission="specification.generate">
  - Envolver "Generate Architecture" com <Protected permission="architecture.generate">
  - _Requirements: 6, 7, 13_

- [x] 13. Testes
  - Criar testes unitários de PermissionService
  - Criar testes de integração de RBAC
  - Criar testes E2E de fluxos por perfil
  - _Requirements: All_

- [x] 13.1 Testes unitários de PermissionService
  - Testar check_permission com diferentes roles
  - Testar super_admin tem todas as permissões
  - Testar cache de permissões
  - _Requirements: 13_

- [x] 13.2 Testes de integração de isolamento multi-tenant
  - Testar que usuário não acessa dados de outro tenant
  - Testar que queries filtram por tenant_id
  - Testar que super_admin acessa todos os tenants
  - _Requirements: 11_

- [x] 13.3 Testes E2E por perfil
  - Testar fluxo de Project Manager
  - Testar fluxo de Developer
  - Testar fluxo de QA
  - Testar que ações sem permissão são bloqueadas
  - _Requirements: 5, 6, 7, 8, 9_

- [ ] 14. Documentação e Migração
  - Criar guia de migração
  - Documentar permissões de cada role
  - Criar guia de uso para admins
  - _Requirements: All_

- [ ] 14.1 Criar guia de migração
  - Documentar passos para migrar dados existentes
  - Documentar como atribuir roles a usuários existentes
  - Criar script de migração de dados
  - _Requirements: All_

- [ ] 14.2 Documentar permissões
  - Criar tabela de permissões por role
  - Documentar como adicionar novas permissões
  - Documentar como criar novos roles
  - _Requirements: 13_

- [ ] 14.3 Criar guia para administradores
  - Documentar como criar empresas
  - Documentar como gerenciar usuários e roles
  - Documentar como visualizar auditoria
  - _Requirements: 2, 3, 4, 12_

- [ ] 15. Limpeza e Organização
  - Mover documentos antigos para pasta old/
  - Organizar documentação
  - Atualizar README principal
  - _Requirements: Maintenance_

- [ ] 15.1 Criar pasta old/ e mover documentos antigos
  - Criar diretório old/
  - Mover documentos de sessões anteriores
  - Mover documentos desnecessários
  - _Requirements: Maintenance_

- [ ] 15.2 Organizar documentação principal
  - Atualizar README.md principal
  - Criar índice de documentação atualizado
  - Manter apenas documentos relevantes na raiz
  - _Requirements: Maintenance_

---

## Execution Order

### Sprint 1 (Fundação - 3-4 dias)
1. Preparar Banco de Dados e Modelos (Task 1)
2. Implementar Serviços Base (Task 2)
3. Criar Roles Padrão e Seed (Task 3)

### Sprint 2 (Backend - 3-4 dias)
4. Implementar Endpoints de Gerenciamento (Task 4)
5. Atualizar JWT com Tenant e Roles (Task 5)
6. Implementar Middleware de Tenant (Task 6)
7. Adicionar Verificação de Permissões (Task 7)
8. Implementar Auditoria (Task 8)

### Sprint 3 (Frontend - 3-4 dias)
9. Frontend - Context e Hooks (Task 9)
10. Frontend - Filtro de Projeto (Task 10)
11. Frontend - Telas de Gerenciamento (Task 11)
12. Frontend - Atualizar Componentes (Task 12)

### Sprint 4 (Testes e Docs - 2-3 dias)
13. Testes (Task 13)
14. Documentação e Migração (Task 14)

---

## Total Estimated Time

- Sprint 1: 3-4 dias
- Sprint 2: 3-4 dias
- Sprint 3: 3-4 dias
- Sprint 4: 2-3 dias

**Total: 11-15 dias de desenvolvimento**

---

**Data**: 24/02/2026  
**Versão**: 1.0  
**Status**: Pronto para Execução
