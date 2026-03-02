# Design Document - RBAC e Multi-Tenant

## Overview

Este documento descreve o design técnico para implementação de um sistema completo de controle de acesso baseado em perfis (RBAC - Role-Based Access Control) e isolamento multi-tenant no Bsmart-ALM. O sistema permitirá que múltiplas empresas usem a plataforma de forma isolada, com controle granular de permissões por perfil de usuário.

### Objetivos Técnicos

1. Implementar isolamento completo de dados por tenant (empresa)
2. Criar sistema de perfis hierárquico e flexível
3. Garantir verificação de permissões em todas as operações
4. Manter performance com cache de permissões
5. Facilitar auditoria com log de ações

---

## Architecture

### Arquitetura em Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  - Context de Permissões                                     │
│  - HOCs de Proteção de Rotas                                 │
│  - Componentes Condicionais por Permissão                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                    │
│  - Middleware de Tenant                                      │
│  - Decorators de Permissão                                   │
│  - Auditoria de Ações                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Camada de Serviços                        │
│  - Permission Service                                        │
│  - Tenant Service                                            │
│  - Audit Service                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Banco de Dados (PostgreSQL)               │
│  - Todas as tabelas com tenant_id                           │
│  - Índices em tenant_id                                      │
│  - Row Level Security (RLS) opcional                         │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Autenticação e Autorização

```
1. Login
   ↓
2. JWT gerado com: user_id, tenant_id, roles[]
   ↓
3. Frontend armazena token e permissões
   ↓
4. Cada request inclui token no header
   ↓
5. Backend valida token e extrai tenant_id
   ↓
6. Middleware injeta tenant_id em todas as queries
   ↓
7. Decorator verifica permissões antes da ação
   ↓
8. Ação executada (se autorizada)
   ↓
9. Log de auditoria registrado
```

---

## Data Models

### Modelo de Dados Completo

#### 1. Tenants (Empresas)

```python
class Tenant(BaseTenantModel, table=True):
    """Empresa/Organização no sistema."""
    __tablename__ = "tenants"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=100, unique=True, index=True)
    domain: Optional[str] = Field(max_length=255, default=None)  # Domínio customizado
    logo_url: Optional[str] = Field(max_length=500, default=None)
    
    # Configurações
    settings: dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Assinatura
    subscription_plan: str = Field(default="free")  # free, basic, premium, enterprise
    subscription_expires_at: Optional[datetime] = None
    max_users: int = Field(default=10)
    max_projects: int = Field(default=5)
    
    # Status
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relacionamentos
    users: List["User"] = Relationship(back_populates="tenant")
    projects: List["Project"] = Relationship(back_populates="tenant")
```

#### 2. Roles (Perfis)

```python
class Role(SQLModel, table=True):
    """Perfis de usuário no sistema."""
    __tablename__ = "roles"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=50, unique=True, index=True)  # super_admin, company_admin, etc
    display_name: str = Field(max_length=100)
    description: Optional[str] = None
    level: int = Field(default=10)  # 1=SuperAdmin, 2=CompanyAdmin, 3=ProjectManager, etc
    
    # Permissões (lista de strings)
    permissions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Configurações
    is_system: bool = Field(default=False)  # Não pode ser deletado
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relacionamentos
    user_roles: List["UserRole"] = Relationship(back_populates="role")
```

#### 3. User Roles (Atribuição de Perfis)

```python
class UserRole(BaseTenantModel, table=True):
    """Atribuição de perfis a usuários."""
    __tablename__ = "user_roles"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role_id: UUID = Field(foreign_key="roles.id", index=True)
    tenant_id: UUID = Field(foreign_key="tenants.id", index=True)
    
    # Escopo (opcional - para perfis específicos de projeto)
    project_id: Optional[UUID] = Field(foreign_key="projects.id", default=None, index=True)
    
    # Metadados
    assigned_by: UUID = Field(foreign_key="users.id")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # Para perfis temporários
    
    # Relacionamentos
    user: "User" = Relationship(back_populates="user_roles")
    role: "Role" = Relationship(back_populates="user_roles")
    project: Optional["Project"] = Relationship()
    
    # Constraint único
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', 'tenant_id', 'project_id', name='uq_user_role_tenant_project'),
    )
```

#### 4. Permissions (Permissões Granulares)

```python
# Permissões são strings no formato: "resource.action"
# Exemplos:
PERMISSIONS = {
    # Super Admin
    'tenant.create',
    'tenant.read',
    'tenant.update',
    'tenant.delete',
    'tenant.*.all',  # Todas as permissões de tenant
    
    # Company Admin
    'user.create',
    'user.read',
    'user.update',
    'user.delete',
    'user.role.assign',
    'project.create',
    'project.read',
    'project.update',
    'project.delete',
    
    # Project Manager
    'project.create',
    'project.read',
    'project.update',
    'project.member.add',
    'project.member.remove',
    'workitem.create',
    'workitem.read',
    'workitem.update',
    'workitem.delete',
    'workitem.assign',
    
    # PO / Analyst
    'document.upload',
    'document.read',
    'requirements.generate',
    'requirements.approve',
    'specification.generate',
    'specification.read',
    
    # Architect
    'specification.read',
    'architecture.generate',
    'architecture.update',
    'architecture.read',
    
    # Developer
    'workitem.read',
    'workitem.update.own',  # Apenas work items atribuídos
    'workitem.status.in_progress',
    'workitem.status.done',
    
    # QA
    'workitem.read',
    'workitem.update.own',
    'workitem.status.approved',
    'workitem.status.rejected',
    'workitem.test',
}
```

#### 5. Audit Log (Log de Auditoria)

```python
class AuditLog(BaseTenantModel, table=True):
    """Log de auditoria de ações no sistema."""
    __tablename__ = "audit_logs"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenants.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    # Ação
    action: str = Field(max_length=100, index=True)  # create_project, delete_user, etc
    resource_type: str = Field(max_length=50, index=True)  # project, user, workitem, etc
    resource_id: Optional[UUID] = Field(default=None, index=True)
    
    # Detalhes
    details: dict = Field(default_factory=dict, sa_column=Column(JSON))
    ip_address: Optional[str] = Field(max_length=45)
    user_agent: Optional[str] = Field(max_length=500)
    
    # Status
    status: str = Field(default="success")  # success, failure, error
    error_message: Optional[str] = None
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relacionamentos
    user: "User" = Relationship()
    tenant: "Tenant" = Relationship()
```

#### 6. Atualização do Modelo User

```python
class User(BaseTenantModel, table=True):
    """Usuário do sistema."""
    __tablename__ = "users"
    
    # ... campos existentes ...
    
    # Novos campos
    is_super_admin: bool = Field(default=False)  # Super Admin global
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    
    # Relacionamentos
    user_roles: List["UserRole"] = Relationship(back_populates="user")
    audit_logs: List["AuditLog"] = Relationship(back_populates="user")
    
    # Método helper
    def has_permission(self, permission: str, project_id: Optional[UUID] = None) -> bool:
        """Verifica se usuário tem permissão."""
        if self.is_super_admin:
            return True
        
        # Verificar permissões dos roles
        for user_role in self.user_roles:
            if project_id and user_role.project_id != project_id:
                continue
            if permission in user_role.role.permissions:
                return True
            if '*' in user_role.role.permissions:  # Wildcard
                return True
        
        return False
```

---

## Components and Interfaces

### Backend Components

#### 1. Permission Service

```python
# services/identity/permission_service.py

class PermissionService:
    """Serviço de gerenciamento de permissões."""
    
    @staticmethod
    async def check_permission(
        user: User,
        permission: str,
        resource_id: Optional[UUID] = None,
        session: AsyncSession = None
    ) -> bool:
        """Verifica se usuário tem permissão."""
        # Super admin tem todas as permissões
        if user.is_super_admin:
            return True
        
        # Verificar permissões dos roles
        query = select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.tenant_id == user.tenant_id
        ).options(selectinload(UserRole.role))
        
        result = await session.execute(query)
        user_roles = result.scalars().all()
        
        for user_role in user_roles:
            if permission in user_role.role.permissions:
                return True
            # Verificar wildcard
            if any(p.endswith('.*') and permission.startswith(p[:-2]) 
                   for p in user_role.role.permissions):
                return True
        
        return False
    
    @staticmethod
    async def get_user_permissions(
        user: User,
        project_id: Optional[UUID] = None,
        session: AsyncSession = None
    ) -> List[str]:
        """Retorna todas as permissões do usuário."""
        if user.is_super_admin:
            return ['*']  # Todas as permissões
        
        permissions = set()
        
        query = select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.tenant_id == user.tenant_id
        )
        
        if project_id:
            query = query.where(
                or_(
                    UserRole.project_id == project_id,
                    UserRole.project_id.is_(None)  # Permissões globais
                )
            )
        
        query = query.options(selectinload(UserRole.role))
        result = await session.execute(query)
        user_roles = result.scalars().all()
        
        for user_role in user_roles:
            permissions.update(user_role.role.permissions)
        
        return list(permissions)
```

#### 2. Tenant Middleware

```python
# services/shared/middleware/tenant_middleware.py

class TenantMiddleware:
    """Middleware para injetar tenant_id em todas as requests."""
    
    async def __call__(self, request: Request, call_next):
        # Extrair tenant_id do token JWT
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            try:
                payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
                tenant_id = payload.get('tenant_id')
                
                # Injetar no request state
                request.state.tenant_id = tenant_id
                request.state.user_id = payload.get('sub')
                request.state.is_super_admin = payload.get('is_super_admin', False)
                
            except JWTError:
                pass
        
        response = await call_next(request)
        return response
```

#### 3. Permission Decorator

```python
# services/identity/decorators.py

def require_permission(permission: str):
    """Decorator para verificar permissão antes de executar função."""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair current_user dos kwargs
            current_user = kwargs.get('current_user')
            session = kwargs.get('session')
            
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            # Verificar permissão
            has_perm = await PermissionService.check_permission(
                user=current_user,
                permission=permission,
                session=session
            )
            
            if not has_perm:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Uso:
@router.post("/projects")
@require_permission("project.create")
async def create_project(...):
    pass
```

#### 4. Audit Service

```python
# services/identity/audit_service.py

class AuditService:
    """Serviço de auditoria de ações."""
    
    @staticmethod
    async def log_action(
        user: User,
        action: str,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        details: dict = None,
        status: str = "success",
        error_message: Optional[str] = None,
        request: Request = None,
        session: AsyncSession = None
    ):
        """Registra ação no log de auditoria."""
        
        audit_log = AuditLog(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get('user-agent') if request else None,
            status=status,
            error_message=error_message
        )
        
        session.add(audit_log)
        await session.commit()
```

### Frontend Components

#### 1. Permission Context

```typescript
// frontend/src/contexts/PermissionContext.tsx

interface PermissionContextType {
  permissions: string[]
  hasPermission: (permission: string) => boolean
  hasAnyPermission: (permissions: string[]) => boolean
  hasAllPermissions: (permissions: string[]) => boolean
  isLoading: boolean
}

export const PermissionProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [permissions, setPermissions] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    loadPermissions()
  }, [])
  
  const loadPermissions = async () => {
    try {
      const { data } = await api.get('/auth/permissions')
      setPermissions(data.permissions)
    } catch (error) {
      console.error('Failed to load permissions:', error)
    } finally {
      setIsLoading(false)
    }
  }
  
  const hasPermission = (permission: string) => {
    if (permissions.includes('*')) return true
    return permissions.includes(permission)
  }
  
  const hasAnyPermission = (perms: string[]) => {
    return perms.some(p => hasPermission(p))
  }
  
  const hasAllPermissions = (perms: string[]) => {
    return perms.every(p => hasPermission(p))
  }
  
  return (
    <PermissionContext.Provider value={{
      permissions,
      hasPermission,
      hasAnyPermission,
      hasAllPermissions,
      isLoading
    }}>
      {children}
    </PermissionContext.Provider>
  )
}
```

#### 2. Protected Component

```typescript
// frontend/src/components/ProtectedComponent.tsx

interface ProtectedProps {
  permission: string | string[]
  fallback?: React.ReactNode
  children: React.ReactNode
}

export const Protected: React.FC<ProtectedProps> = ({ 
  permission, 
  fallback = null, 
  children 
}) => {
  const { hasPermission, hasAnyPermission } = usePermissions()
  
  const allowed = Array.isArray(permission)
    ? hasAnyPermission(permission)
    : hasPermission(permission)
  
  if (!allowed) return <>{fallback}</>
  
  return <>{children}</>
}

// Uso:
<Protected permission="project.create">
  <button onClick={createProject}>Create Project</button>
</Protected>
```

#### 3. Project Selector Component

```typescript
// frontend/src/components/ProjectSelector.tsx

export const ProjectSelector: React.FC<{
  value: string
  onChange: (projectId: string) => void
}> = ({ value, onChange }) => {
  const [projects, setProjects] = useState<Project[]>([])
  
  useEffect(() => {
    loadProjects()
  }, [])
  
  const loadProjects = async () => {
    const { data } = await api.get('/projects')
    setProjects(data)
  }
  
  const handleChange = (projectId: string) => {
    onChange(projectId)
    localStorage.setItem('lastSelectedProject', projectId)
  }
  
  return (
    <select value={value} onChange={(e) => handleChange(e.target.value)}>
      <option value="">All Projects</option>
      {projects.map(project => (
        <option key={project.id} value={project.id}>
          {project.name}
        </option>
      ))}
    </select>
  )
}
```

---

## Error Handling

### Tipos de Erros

```python
class PermissionDeniedError(HTTPException):
    """Erro quando usuário não tem permissão."""
    def __init__(self, permission: str):
        super().__init__(
            status_code=403,
            detail=f"Permission denied: {permission}"
        )

class TenantIsolationError(HTTPException):
    """Erro quando tentativa de acessar dados de outro tenant."""
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Access denied: resource belongs to another organization"
        )

class RoleNotFoundError(HTTPException):
    """Erro quando role não existe."""
    def __init__(self, role_name: str):
        super().__init__(
            status_code=404,
            detail=f"Role not found: {role_name}"
        )
```

### Tratamento no Frontend

```typescript
// frontend/src/api/client.ts

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403) {
      // Permissão negada
      toast.error('You do not have permission to perform this action')
    } else if (error.response?.status === 401) {
      // Não autenticado
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

---

## Testing Strategy

### Testes Unitários

```python
# tests/test_permission_service.py

async def test_super_admin_has_all_permissions():
    user = User(is_super_admin=True)
    assert await PermissionService.check_permission(user, 'any.permission')

async def test_user_with_role_has_permission():
    user = create_user_with_role('developer')
    assert await PermissionService.check_permission(user, 'workitem.read')
    assert not await PermissionService.check_permission(user, 'project.delete')

async def test_tenant_isolation():
    user1 = create_user(tenant_id=tenant1_id)
    user2 = create_user(tenant_id=tenant2_id)
    
    project = create_project(tenant_id=tenant1_id)
    
    # User1 pode acessar
    assert can_access_project(user1, project)
    
    # User2 não pode acessar
    assert not can_access_project(user2, project)
```

### Testes de Integração

```python
# tests/test_rbac_integration.py

async def test_create_project_requires_permission(client):
    # Usuário sem permissão
    token = create_token_for_user(user_without_permission)
    response = await client.post(
        '/projects',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Test Project'}
    )
    assert response.status_code == 403

async def test_tenant_isolation_in_queries(client):
    # Criar projetos em tenants diferentes
    project1 = create_project(tenant_id=tenant1_id)
    project2 = create_project(tenant_id=tenant2_id)
    
    # User do tenant1 só vê projeto do tenant1
    token = create_token_for_user(user_tenant1)
    response = await client.get(
        '/projects',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    projects = response.json()
    assert len(projects) == 1
    assert projects[0]['id'] == str(project1.id)
```

### Testes E2E

```typescript
// tests/e2e/rbac.spec.ts

describe('RBAC', () => {
  it('should hide create project button for users without permission', () => {
    loginAs('developer')
    visit('/projects')
    cy.get('[data-testid="create-project-btn"]').should('not.exist')
  })
  
  it('should show create project button for project managers', () => {
    loginAs('project_manager')
    visit('/projects')
    cy.get('[data-testid="create-project-btn"]').should('be.visible')
  })
  
  it('should filter work items by selected project', () => {
    loginAs('developer')
    visit('/work-items')
    
    // Selecionar projeto
    cy.get('[data-testid="project-selector"]').select('Project A')
    
    // Verificar que apenas work items do projeto aparecem
    cy.get('[data-testid="work-item"]').each(($el) => {
      expect($el).to.have.attr('data-project-id', 'project-a-id')
    })
  })
})
```

---

## Performance Considerations

### Cache de Permissões

```python
# services/identity/permission_cache.py

from functools import lru_cache
from cachetools import TTLCache

# Cache de permissões por usuário (TTL de 5 minutos)
permission_cache = TTLCache(maxsize=1000, ttl=300)

async def get_cached_permissions(user_id: UUID, session: AsyncSession) -> List[str]:
    """Retorna permissões do cache ou carrega do banco."""
    cache_key = f"permissions:{user_id}"
    
    if cache_key in permission_cache:
        return permission_cache[cache_key]
    
    permissions = await PermissionService.get_user_permissions(user_id, session)
    permission_cache[cache_key] = permissions
    
    return permissions

def invalidate_user_permissions(user_id: UUID):
    """Invalida cache de permissões do usuário."""
    cache_key = f"permissions:{user_id}"
    if cache_key in permission_cache:
        del permission_cache[cache_key]
```

### Índices de Banco de Dados

```sql
-- Índices para performance

-- tenant_id em todas as tabelas
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_projects_tenant_id ON projects(tenant_id);
CREATE INDEX idx_work_items_tenant_id ON work_items(tenant_id);
CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);

-- user_roles para lookup rápido
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_tenant_id ON user_roles(tenant_id);
CREATE INDEX idx_user_roles_project_id ON user_roles(project_id);

-- audit_logs para queries de auditoria
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- Índice composto para queries comuns
CREATE INDEX idx_work_items_project_status ON work_items(project_id, status);
CREATE INDEX idx_work_items_assignee ON work_items(assigned_to, status);
```

---

## Migration Strategy

### Fase 1: Preparação (Sem Breaking Changes)

1. Criar novas tabelas: roles, user_roles, audit_logs
2. Adicionar campos novos em users: is_super_admin, last_login_at
3. Melhorar tabela tenants com novos campos
4. Criar índices

### Fase 2: Migração de Dados

1. Criar roles padrão (super_admin, company_admin, etc)
2. Migrar usuários existentes para roles apropriados
3. Atribuir tenant_id a todos os registros existentes

### Fase 3: Implementação de Código

1. Implementar PermissionService
2. Adicionar decorators de permissão
3. Atualizar rotas com verificação de permissão
4. Implementar middleware de tenant

### Fase 4: Frontend

1. Criar PermissionContext
2. Adicionar componente Protected
3. Atualizar páginas com verificação de permissão
4. Adicionar ProjectSelector

### Fase 5: Testes e Validação

1. Testes unitários
2. Testes de integração
3. Testes E2E
4. Testes de carga

---

## Security Considerations

### Princípios de Segurança

1. **Least Privilege**: Usuários têm apenas permissões necessárias
2. **Defense in Depth**: Verificação em múltiplas camadas (frontend + backend)
3. **Fail Secure**: Em caso de erro, negar acesso
4. **Audit Everything**: Log de todas as ações sensíveis

### Checklist de Segurança

- [ ] Todas as queries filtram por tenant_id
- [ ] Todas as rotas verificam permissões
- [ ] JWT inclui tenant_id e roles
- [ ] Frontend oculta ações sem permissão
- [ ] Auditoria de ações sensíveis
- [ ] Rate limiting por tenant
- [ ] Validação de input em todas as rotas
- [ ] Sanitização de dados antes de salvar

---

**Data**: 24/02/2026  
**Versão**: 1.0  
**Status**: Completo
