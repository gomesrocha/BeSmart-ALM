# 🚨 Correções Urgentes - Frontend Bsmart-ALM

## 📋 Problemas Identificados

### 1. ❌ Botão "Criar Projeto" Sumiu
**Sintoma:** Botão não aparece na tela de Projects  
**Causa:** Componente `<Protected permission="project:create">` não está mostrando o botão  
**Impacto:** Impossível criar novos projetos

### 2. ❌ Não Consegue Atribuir Permissões em User Roles
**Sintoma:** Tanto superadmin quanto tenant admin não conseguem atribuir roles  
**Causa:** Usuários não têm permissões retornadas pela API  
**Impacto:** Impossível gerenciar usuários

### 3. ❌ Criar Tenant Não Atribui Admin Automaticamente
**Sintoma:** Ao criar tenant com usuário, não vira admin automaticamente  
**Causa:** Backend não está atribuindo role "Tenant Admin" ao criar  
**Impacto:** Usuário criado não tem permissões

## 🔧 Soluções

### Solução 1: Corrigir Permissões no Backend
**Arquivo:** `services/identity/tenant_service.py`

Quando criar tenant, automaticamente:
1. Criar role "Tenant Admin" para o tenant
2. Atribuir role ao usuário admin
3. Garantir que tem todas as permissões necessárias

### Solução 2: Corrigir Endpoint de Permissões
**Arquivo:** `services/identity/router.py`

Garantir que `/auth/permissions` retorna:
- Todas as permissões do usuário
- Roles com suas permissões
- Flag is_super_admin correta

### Solução 3: Fallback no Frontend (Temporário)
**Arquivo:** `frontend/src/contexts/PermissionContext.tsx`

Enquanto backend não está 100%, dar permissões básicas:
- Todos os usuários: `project:create`, `project:read`
- Tenant Admins: todas as permissões do tenant
- Super Admins: todas as permissões

## 📝 Ordem de Implementação

1. ✅ Corrigir criação de tenant (atribuir admin automaticamente)
2. ✅ Corrigir endpoint de permissões (retornar permissões corretas)
3. ✅ Atualizar senha do gomesrocha para gomes1234
4. ✅ Testar fluxo completo

## 🧪 Como Testar

```bash
# 1. Criar novo tenant
# Via frontend: Tenants → Create Tenant
# Email: teste@teste.com
# Password: teste1234

# 2. Verificar se virou admin
uv run python scripts/check_user_permissions.py teste@teste.com

# 3. Fazer login e verificar se vê botão "Criar Projeto"
# 4. Criar projeto e verificar se funciona
```

## 🎯 Status

- [ ] Correção 1: Criar tenant atribui admin
- [ ] Correção 2: Endpoint de permissões funciona
- [ ] Correção 3: Senha gomesrocha atualizada
- [ ] Correção 4: Botão criar projeto aparece
- [ ] Correção 5: User roles funciona

## 📊 Próximos Passos

Após correções:
1. Testar com acme@acme.com
2. Testar com gomesrocha@bsmart.com
3. Criar novo tenant e testar
4. Testar AI Orchestrator
5. Testar Plugin VSCode
