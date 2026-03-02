# Correção: is_superuser vs is_super_admin

## Problema Identificado

O botão de criar projeto sumiu para o usuário `gomesrocha` (superadmin) porque havia uma inconsistência no código:

- O modelo `User` tem o campo `is_superuser`
- Mas vários lugares do código estavam verificando `is_super_admin`

Isso fazia com que o sistema não reconhecesse corretamente os superadmins.

## Arquivos Corrigidos

### 1. `services/identity/permission_service.py`
- Linha 67: `is_super_admin` → `is_superuser`
- Linha 157: `is_super_admin` → `is_superuser`

### 2. `services/identity/router.py`
- Linha 157: `is_super_admin` → `is_superuser`

### 3. `services/identity/role_router.py`
- Linha 414: `is_super_admin` → `is_superuser`

### 4. `services/identity/dependencies.py`
- Removido código que tentava adicionar atributo `is_super_admin` ao objeto user
- O campo `is_superuser` já existe no modelo

## Como Testar

1. Reinicie o backend:
```bash
# Parar o backend atual (Ctrl+C)
# Iniciar novamente
./start_bsmart.sh
```

2. Faça login com o usuário `gomesrocha`

3. Verifique se o botão "New Project" aparece na página de Projects

## Nota Importante

O token JWT inclui `is_super_admin` (com underscore), mas o modelo User usa `is_superuser`. Isso é intencional:
- O token usa `is_super_admin` para ser mais explícito
- O modelo usa `is_superuser` seguindo convenções do Django/FastAPI
- O código agora faz a conversão correta entre os dois

## Impacto

Esta correção garante que:
- Superadmins tenham TODAS as permissões (retorna `["*"]`)
- O botão de criar projeto apareça para superadmins
- Todas as verificações de permissão funcionem corretamente
