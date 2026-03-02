# 👥 User Management Guide

## ✨ Nova Funcionalidade: Gestão de Usuários!

Agora você pode gerenciar usuários da sua organização diretamente pelo frontend!

## 🎯 O que foi implementado

### Backend (1 novo arquivo)

1. **`services/identity/user_router.py`**
   - `GET /api/v1/users` - Listar usuários
   - `POST /api/v1/users` - Criar usuário
   - `GET /api/v1/users/{id}` - Ver usuário
   - `PATCH /api/v1/users/{id}` - Editar usuário
   - `DELETE /api/v1/users/{id}` - Desativar usuário

### Frontend (3 arquivos atualizados)

1. **`frontend/src/pages/Users.tsx`** - Página de gestão de usuários
2. **`frontend/src/App.tsx`** - Rota adicionada
3. **`frontend/src/components/Sidebar.tsx`** - Link no menu

## 🚀 Funcionalidades

### 1. Listar Usuários
- Ver todos os usuários da organização
- Status (Active/Inactive)
- Badge de Admin para superusers
- Data de último login
- Data de criação

### 2. Criar Usuário
- Email (único)
- Nome completo
- Senha
- Status (Active/Inactive)

### 3. Editar Usuário
- Atualizar email
- Atualizar nome
- Mudar senha (opcional)
- Ativar/Desativar

### 4. Desativar Usuário
- Soft delete (desativa ao invés de deletar)
- Não pode desativar a si mesmo
- Confirmação antes de desativar

### 5. Busca
- Buscar por email
- Buscar por nome
- Busca em tempo real

## 📝 Como Usar

### Acessar Gestão de Usuários

1. **Login**: http://localhost:3000
2. **Clicar em "Users"** no menu lateral
3. Ver lista de usuários

### Criar Novo Usuário

1. Clicar em "New User"
2. Preencher formulário:
   - Email: user@example.com
   - Full Name: John Doe
   - Password: senha123
   - Active: ✓ (marcado)
3. Clicar em "Create User"

### Editar Usuário

1. Clicar no ícone de editar (lápis)
2. Modificar campos desejados
3. Senha é opcional (deixar em branco para manter atual)
4. Clicar em "Update User"

### Desativar Usuário

1. Clicar no ícone de deletar (lixeira)
2. Confirmar ação
3. Usuário será desativado (não deletado)

### Buscar Usuário

1. Digitar no campo de busca
2. Busca por email ou nome
3. Resultados filtrados em tempo real

## 🔒 Permissões

### Criar Usuário
- Requer permissão: `user:create`
- Apenas admins por padrão

### Editar Usuário
- Requer permissão: `user:update`
- Apenas admins por padrão

### Desativar Usuário
- Requer permissão: `user:delete`
- Apenas admins por padrão
- Não pode desativar a si mesmo

### Listar Usuários
- Todos os usuários autenticados
- Vê apenas usuários do mesmo tenant

## 🎨 Interface

### Tabela de Usuários

```
┌─────────────────────────────────────────────────────────────┐
│ User              │ Status  │ Last Login │ Created │ Actions│
├─────────────────────────────────────────────────────────────┤
│ 👤 John Doe       │ Active  │ 2024-02-23 │ 2024-01 │ ✏️ 🗑️  │
│    john@test.com  │ Admin   │            │         │        │
├─────────────────────────────────────────────────────────────┤
│ 👤 Jane Smith     │ Active  │ Never      │ 2024-02 │ ✏️ 🗑️  │
│    jane@test.com  │         │            │         │        │
└─────────────────────────────────────────────────────────────┘
```

### Formulário de Criação/Edição

```
┌─────────────────────────────────────┐
│ Create New User                     │
├─────────────────────────────────────┤
│ Email:        [user@example.com   ] │
│ Full Name:    [John Doe           ] │
│ Password:     [••••••••           ] │
│ ☑ Active                            │
│                                     │
│ [Create User] [Cancel]              │
└─────────────────────────────────────┘
```

## 🔧 API Endpoints

### Listar Usuários
```bash
GET /api/v1/users
Authorization: Bearer <token>
```

**Resposta**:
```json
[
  {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_superuser": false,
    "tenant_id": "uuid",
    "created_at": "2024-02-23T10:00:00",
    "last_login": "2024-02-23T14:00:00"
  }
]
```

### Criar Usuário
```bash
POST /api/v1/users
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "senha123",
  "full_name": "New User",
  "is_active": true
}
```

### Editar Usuário
```bash
PATCH /api/v1/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "updated@example.com",
  "full_name": "Updated Name",
  "is_active": true,
  "password": "newpassword"  // opcional
}
```

### Desativar Usuário
```bash
DELETE /api/v1/users/{user_id}
Authorization: Bearer <token>
```

## 🐛 Troubleshooting

### Erro: "Email already registered"
**Causa**: Email já está em uso
**Solução**: Usar outro email

### Erro: "Cannot delete yourself"
**Causa**: Tentando desativar o próprio usuário
**Solução**: Pedir para outro admin desativar

### Erro: "User not found"
**Causa**: Usuário não existe ou é de outro tenant
**Solução**: Verificar ID do usuário

### Não vejo o menu "Users"
**Causa**: Falta reiniciar o frontend
**Solução**: Reiniciar o frontend (Ctrl+C e `npm run dev`)

## 📊 Próximas Funcionalidades

### Em Desenvolvimento
- ✅ Gestão de usuários
- 🔄 Edição de projetos
- 🔄 Gestão de membros do projeto
- 🔄 Perfil do usuário

### Planejadas
- Atribuir roles aos usuários
- Gerenciar permissões
- Histórico de atividades
- Exportar lista de usuários
- Importar usuários em lote

## ✅ Checklist

- [ ] Backend reiniciado
- [ ] Frontend reiniciado
- [ ] Acessar http://localhost:3000
- [ ] Login como admin
- [ ] Clicar em "Users" no menu
- [ ] Criar novo usuário
- [ ] Editar usuário
- [ ] Buscar usuário
- [ ] Desativar usuário

## 🎉 Resultado

Agora você tem gestão completa de usuários:

✅ Listar todos os usuários
✅ Criar novos usuários
✅ Editar usuários existentes
✅ Desativar usuários
✅ Buscar usuários
✅ Interface intuitiva
✅ Validações de segurança

**Gestão de usuários implementada com sucesso!** 👥
