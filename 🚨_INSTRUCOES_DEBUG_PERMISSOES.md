# Instruções para Debug de Permissões

## Problema

O botão "New Project" e outras funcionalidades somem intermitentemente para os usuários gomesrocha e acme.

## Correções Aplicadas Agora

1. **Adicionadas permissões faltantes** no PermissionContext:
   - `work_item:transition`
   - `work_item:approve`
   - `requirements:*`
   - `architecture:*`
   - `code:*`

2. **Adicionados logs detalhados** em:
   - `PermissionContext.tsx` - logs de carregamento de permissões
   - `Protected.tsx` - logs quando bloqueia/permite conteúdo

## Como Testar AGORA

### Passo 1: Limpar TUDO
```
1. Abra o DevTools (F12)
2. Vá em Application > Storage > Clear site data
3. Feche o navegador completamente
4. Abra novamente
```

### Passo 2: Fazer Login e Verificar Console
```
1. Abra o DevTools (F12) ANTES de fazer login
2. Vá na aba Console
3. Faça login com gomesrocha
4. Observe os logs no console
```

### Passo 3: Verificar Logs Esperados

Você DEVE ver no console:

```
🔄 Fetching permissions...
👤 User info: { email: "gomesrocha@example.com", is_superuser: true }
📋 Permissions API Response: { ... }
🔓 MODO DESENVOLVIMENTO: Dando TODAS as permissões para TODOS os usuários
   User: gomesrocha@example.com | is_superuser: true
   Timestamp: 2026-02-28T...
📋 Setting permissions array with 30 permissions
👥 Setting roles: X roles
🔐 Setting isSuperAdmin: true
✅ Permissions granted: {
  total: 30,
  has_project_create: true,
  has_user_role_assign: true,
  has_work_item_transition: true,
  ...
}
🔍 Verificação pós-set:
   permissions state será: 30 items
   roles state será: X items
   isSuperAdmin state será: true
✅ Loading complete - isLoading set to FALSE
```

### Passo 4: Verificar Componente Protected

Quando a página Projects carregar, você deve ver:

```
✅ Protected: ALLOWED - has permission "project:create"
```

Se você ver:
```
🔒 Protected: BLOCKED - missing permission "project:create"
```

Então há um problema!

## Se o Botão AINDA Sumir

### Cenário 1: isLoading fica true para sempre
**Sintoma**: Console mostra "🔒 Protected: isLoading=true, hiding content"

**Solução**:
- Há um erro na chamada da API `/auth/permissions`
- Verifique se o backend está rodando
- Verifique se há erros de rede no console

### Cenário 2: Permissões não são setadas
**Sintoma**: Console mostra "🔒 Protected: BLOCKED - missing permission"

**Solução**:
- O array de permissões não foi setado corretamente
- Verifique se você vê "📋 Setting permissions array with 30 permissions"
- Se não vê, há um erro no código do PermissionContext

### Cenário 3: Cache do navegador
**Sintoma**: Logs antigos aparecem no console

**Solução**:
```bash
# Limpar cache do navegador de forma agressiva
1. Ctrl+Shift+Delete
2. Selecionar "Cached images and files"
3. Selecionar "All time"
4. Clear data
5. Fechar e reabrir navegador
```

### Cenário 4: Token JWT expirando
**Sintoma**: Funciona por alguns minutos, depois para

**Solução**:
- O token JWT está expirando e o refresh não está funcionando
- Verifique o tempo de expiração no .env (JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
- Faça logout e login novamente

## Informações para Reportar

Se o problema persistir, me envie:

1. **Todos os logs do console** (copie e cole)
2. **Qual usuário** está tendo problema (gomesrocha ou acme)
3. **Quando acontece** (logo após login, depois de alguns minutos, etc)
4. **O que você fez** antes do problema aparecer
5. **Screenshot** da tela e do console

## Arquivos Modificados Nesta Sessão

1. `frontend/src/contexts/PermissionContext.tsx` - Logs detalhados + permissões adicionadas
2. `frontend/src/components/Protected.tsx` - Logs de bloqueio/permissão
3. `services/identity/permission_service.py` - Corrigido is_superuser
4. `services/identity/router.py` - Corrigido is_superuser
5. `services/identity/role_router.py` - Corrigido is_superuser
6. `services/identity/dependencies.py` - Removido código desnecessário

## Próxima Sessão

Se o problema continuar, vamos:
1. Adicionar logs no backend para ver o que está sendo retornado
2. Criar um endpoint de debug que mostra todas as permissões
3. Verificar se há algum middleware interferindo
4. Considerar remover completamente o sistema de permissões temporariamente
