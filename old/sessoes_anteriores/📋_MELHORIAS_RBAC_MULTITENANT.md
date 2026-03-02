# 📋 Melhorias: RBAC e Multi-Tenant Completo

## 🎯 Objetivos

1. **Filtro de Work Items por Projeto**
2. **Sistema de Perfis (RBAC) Completo**
3. **Multi-Tenant Real (Empresas)**

---

## 1️⃣ Filtro de Work Items por Projeto

### Problema Atual:
- Work Items mostra todos os items de todos os projetos
- Difícil de organizar

### Solução:
- Adicionar dropdown de seleção de projeto
- Filtrar work items pelo projeto selecionado
- Salvar última seleção no localStorage

### Implementação:

**Frontend: `frontend/src/pages/WorkItems.tsx`**
```typescript
const [selectedProject, setSelectedProject] = useState<string>('')

// Carregar último projeto selecionado
useEffect(() => {
  const lastProject = localStorage.getItem('lastSelectedProject')
  if (lastProject) setSelectedProject(lastProject)
}, [])

// Salvar seleção
const handleProjectChange = (projectId: string) => {
  setSelectedProject(projectId)
  localStorage.setItem('lastSelectedProject', projectId)
}

// Filtrar work items
const filteredWorkItems = workItems.filter(item => 
  !selectedProject || item.project_id === selectedProject
)
```

---

## 2️⃣ Sistema de Perfis (RBAC)

### Hierarquia de Perfis:

```
1. Super Admin (Administrador Geral)
   └─ Cadastra empresas
   └─ Cadastra administradores de empresa
   └─ Acesso total ao sistema

2. Company Admin (Administrador da Empresa)
   └─ Cadastra usuários da empresa
   └─ Atribui perfis
   └─ Cria projetos
   └─ Gerencia tudo da empresa

3. Project Manager (Gerente de Projetos)
   └─ Cria projetos
   └─ Adiciona usuários ao projeto
   └─ Gerencia work items

4. PO / Requirements Analyst
   └─ Upload de documentos
   └─ Gerar requisitos
   └─ Gerar especificações
   └─ Aprovar requisitos

5. Architect (Analista)
   └─ Gerar arquitetura
   └─ Revisar especificações

6. Developer (Desenvolvedor)
   └─ Pegar work items
   └─ Implementar
   └─ Mudar status para "Done"

7. QA (Tester)
   └─ Pegar work items para teste
   └─ Aprovar/Rejeitar
```

### Modelo de Dados:

**Tabela: `roles`**
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    description TEXT,
    level INTEGER, -- 1=SuperAdmin, 2=CompanyAdmin, 3=ProjectManager, etc
    permissions JSONB,
    created_at TIMESTAMP
);
```

**Tabela: `user_roles`**
```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    role_id UUID REFERENCES roles(id),
    tenant_id UUID REFERENCES tenants(id),
    project_id UUID REFERENCES projects(id), -- NULL = role global na empresa
    created_at TIMESTAMP,
    UNIQUE(user_id, role_id, tenant_id, project_id)
);
```

### Permissões por Perfil:

```python
PERMISSIONS = {
    'super_admin': [
        'tenant.create',
        'tenant.read',
        'tenant.update',
        'tenant.delete',
        '*', # Todas as permissões
    ],
    'company_admin': [
        'user.create',
        'user.read',
        'user.update',
        'user.delete',
        'project.create',
        'project.read',
        'project.update',
        'project.delete',
        'role.assign',
    ],
    'project_manager': [
        'project.create',
        'project.read',
        'project.update',
        'project.member.add',
        'project.member.remove',
        'workitem.create',
        'workitem.read',
        'workitem.update',
        'workitem.assign',
    ],
    'po_analyst': [
        'project.read',
        'document.upload',
        'requirements.generate',
        'specification.generate',
        'requirements.approve',
        'workitem.read',
    ],
    'architect': [
        'project.read',
        'specification.read',
        'architecture.generate',
        'architecture.update',
        'workitem.read',
    ],
    'developer': [
        'project.read',
        'workitem.read',
        'workitem.update_own', # Só work items atribuídos a ele
        'workitem.status.in_progress',
        'workitem.status.done',
    ],
    'qa': [
        'project.read',
        'workitem.read',
        'workitem.update_own',
        'workitem.status.approved',
        'workitem.status.rejected',
    ],
}
```

---

## 3️⃣ Multi-Tenant Real (Empresas)

### Modelo de Dados:

**Tabela: `tenants` (já existe, melhorar)**
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255), -- Domínio customizado (opcional)
    logo_url VARCHAR(500),
    settings JSONB,
    subscription_plan VARCHAR(50), -- free, basic, premium
    subscription_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Tabela: `tenant_admins`**
```sql
CREATE TABLE tenant_admins (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP,
    UNIQUE(tenant_id, user_id)
);
```

### Fluxo de Cadastro:

```
1. Super Admin cria Tenant (Empresa)
   ├─ Nome da empresa
   ├─ Slug (URL amigável)
   └─ Plano de assinatura

2. Super Admin cria Company Admin
   ├─ Email
   ├─ Nome
   └─ Vincula ao Tenant

3. Company Admin faz login
   ├─ Vê apenas sua empresa
   ├─ Cadastra usuários
   └─ Atribui perfis

4. Usuários fazem login
   ├─ Veem apenas dados da empresa
   └─ Ações limitadas por perfil
```

### Isolamento de Dados:

**Todas as queries devem filtrar por `tenant_id`:**

```python
# Exemplo
@router.get("/projects")
async def list_projects(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    query = select(Project).where(
        Project.tenant_id == current_user.tenant_id  # SEMPRE!
    )
    result = await session.execute(query)
    return result.scalars().all()
```

---

## 📊 Estrutura de Implementação

### Fase 1: Multi-Tenant (1-2 dias)
- [ ] Melhorar modelo Tenant
- [ ] Criar tela de cadastro de empresas (Super Admin)
- [ ] Criar tela de cadastro de Company Admin
- [ ] Garantir isolamento em TODAS as queries
- [ ] Testes de isolamento

### Fase 2: RBAC (2-3 dias)
- [ ] Criar tabelas de roles e user_roles
- [ ] Implementar sistema de permissões
- [ ] Criar decorators de verificação de permissão
- [ ] Atualizar frontend para mostrar/ocultar ações por perfil
- [ ] Tela de gerenciamento de perfis

### Fase 3: Filtro de Work Items (1 dia)
- [ ] Adicionar dropdown de projeto
- [ ] Implementar filtro
- [ ] Salvar última seleção
- [ ] Melhorar UX

### Fase 4: Testes e Ajustes (1 dia)
- [ ] Testar todos os perfis
- [ ] Testar isolamento multi-tenant
- [ ] Ajustar permissões
- [ ] Documentação

---

## 🎯 Priorização

### Urgente (Fazer Agora):
1. ✅ Filtro de Work Items por Projeto
2. ✅ Isolamento Multi-Tenant em queries

### Importante (Próxima Sprint):
3. ✅ Sistema de Perfis (RBAC)
4. ✅ Tela de gerenciamento de empresas

### Desejável (Futuro):
5. ⏳ Planos de assinatura
6. ⏳ Domínios customizados
7. ⏳ White-label

---

## 💡 Sugestões de Melhoria

### UX:
- Breadcrumbs: Empresa > Projeto > Work Item
- Seletor de empresa (se usuário tiver acesso a múltiplas)
- Avatar com iniciais do usuário
- Badge de perfil no header

### Segurança:
- Auditoria de ações (quem fez o quê)
- Log de acessos
- 2FA para admins
- Sessões por dispositivo

### Performance:
- Cache de permissões
- Índices em tenant_id
- Paginação em todas as listas

---

## 📝 Próximos Passos

Quer que eu:

1. **Comece pelo filtro de Work Items?** (mais rápido, 1-2 horas)
2. **Implemente RBAC completo?** (mais complexo, 2-3 dias)
3. **Crie uma spec detalhada primeiro?** (recomendado para RBAC)

Me diga por onde prefere começar! 🚀

---

**Data**: 24/02/2026  
**Status**: 📋 Planejado  
**Complexidade**: Alta  
**Tempo Estimado**: 5-7 dias
