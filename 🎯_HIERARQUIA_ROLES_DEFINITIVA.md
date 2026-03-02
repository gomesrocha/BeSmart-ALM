# Hierarquia de Roles Definitiva

## Estrutura de Permissões

### 1. Superuser (gomesrocha)
**Escopo**: Global (todos os tenants)
**Pode fazer TUDO**:
- ✅ Criar/editar/deletar tenants
- ✅ Criar/editar/deletar usuários (qualquer tenant)
- ✅ Atribuir qualquer permissão/role
- ✅ Criar/editar/deletar projetos (qualquer tenant)
- ✅ Gerenciar work items
- ✅ Gerar requisitos, arquitetura, código
- ✅ Ver todas as telas de administração

### 2. Admin do Tenant (acme)
**Escopo**: Apenas seu tenant
**Pode fazer TUDO no seu tenant**:
- ✅ Criar/editar/deletar usuários do tenant
- ✅ Atribuir permissões/roles no tenant
- ✅ Criar/editar/deletar projetos do tenant
- ✅ Gerenciar work items do tenant
- ✅ Gerar requisitos, arquitetura, código
- ❌ NÃO pode criar/editar outros tenants
- ❌ NÃO pode ver/editar usuários de outros tenants

### 3. Gerente de Projetos
**Escopo**: Projetos específicos
**Permissões**:
- ✅ Criar projetos
- ✅ Editar/deletar seus projetos
- ✅ Adicionar usuários ao projeto
- ✅ Atribuir usuários a work items do projeto
- ✅ Gerenciar work items do projeto
- ✅ Gerar requisitos, arquitetura, código
- ❌ NÃO pode criar usuários
- ❌ NÃO pode atribuir roles globais

### 4. Analista de Requisitos
**Escopo**: Projetos onde está atribuído
**Permissões**:
- ✅ Gerar requisitos
- ✅ Editar requisitos
- ✅ Ver projetos
- ✅ Ver work items
- ❌ NÃO pode criar projetos
- ❌ NÃO pode gerenciar usuários

### 5. Arquiteto
**Escopo**: Projetos onde está atribuído
**Permissões**:
- ✅ Gerar especificação
- ✅ Gerar arquitetura
- ✅ Editar especificação/arquitetura
- ✅ Ver projetos
- ✅ Ver work items
- ❌ NÃO pode criar projetos
- ❌ NÃO pode gerenciar usuários

### 6. Desenvolvedor
**Escopo**: Projetos onde está atribuído
**Permissões**:
- ✅ Ver projetos
- ✅ Pegar work items
- ✅ Mover work items (Draft → In Progress → Done)
- ✅ Adicionar comentários
- ✅ Marcar como concluído
- ✅ Gerar código
- ❌ NÃO pode criar projetos
- ❌ NÃO pode criar work items
- ❌ NÃO pode gerenciar usuários

### 7. Visualizador
**Escopo**: Projetos onde foi convidado
**Permissões**:
- ✅ Ver projetos
- ✅ Ver work items
- ✅ Ver requisitos/arquitetura/código
- ❌ NÃO pode editar nada
- ❌ NÃO pode criar nada
- ❌ NÃO pode mover work items

## Mapeamento de Permissões

### Superuser
```
ALL (*)
```

### Admin do Tenant
```
tenant:read, tenant:update (apenas seu tenant)
user:read, user:write, user:delete (apenas seu tenant)
user:role:assign, user:role:remove, user:role:read
project:create, project:read, project:update, project:delete
work_item:create, work_item:read, work_item:update, work_item:delete, work_item:transition
requirements:create, requirements:read, requirements:update
architecture:create, architecture:read, architecture:update
code:generate, code:read
```

### Gerente de Projetos
```
project:create, project:read, project:update, project:delete (seus projetos)
project:user:assign (adicionar usuários ao projeto)
work_item:create, work_item:read, work_item:update, work_item:delete, work_item:transition
requirements:create, requirements:read, requirements:update
architecture:create, architecture:read, architecture:update
code:generate, code:read
```

### Analista de Requisitos
```
project:read
work_item:read
requirements:create, requirements:read, requirements:update
```

### Arquiteto
```
project:read
work_item:read
requirements:read
architecture:create, architecture:read, architecture:update
```

### Desenvolvedor
```
project:read
work_item:read, work_item:update, work_item:transition (apenas seus work items)
requirements:read
architecture:read
code:generate, code:read
```

### Visualizador
```
project:read
work_item:read
requirements:read
architecture:read
code:read
```

## Implementação

### 1. Backend: Criar roles no banco
- Script para criar todos os roles
- Script para atribuir permissões corretas a cada role

### 2. Frontend: Verificação consistente
- Sempre verificar `is_superuser` PRIMEIRO
- Se não for superuser, verificar permissões específicas
- NUNCA misturar verificação de roles com permissões

### 3. Testes
- Testar cada role individualmente
- Garantir que mudança em um não quebra outro
- Criar testes automatizados
