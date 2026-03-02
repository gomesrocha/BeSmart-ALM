# 🔄 Guia de Reset do Banco de Dados

## Problema

Quando você adiciona novos models (como ProjectSpecification e ProjectArchitecture), o SQLModel pode ter problemas com a ordem de criação das tabelas devido às foreign keys.

## Solução

Resetar o banco de dados e recriar todas as tabelas na ordem correta.

---

## 🚀 Como Resetar o Banco

### Opção 1: Script Automático (Recomendado)

```bash
# Executar script de reset
./scripts/recreate_db.sh
```

O script vai:
1. Pedir confirmação
2. Dropar todas as tabelas
3. Recriar todas as tabelas
4. Fazer seed com dados iniciais

### Opção 2: Manual

```bash
# Executar script Python diretamente
python scripts/reset_and_seed.py
```

---

## 📋 Credenciais Após Reset

Após o reset, use estas credenciais para login:

```
Admin:    admin@example.com / admin123
Dev:      dev@example.com / dev123
PO:       po@example.com / po123
```

---

## 🔧 O Que o Script Faz

1. **Drop Schema**: Remove todas as tabelas
   ```sql
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   ```

2. **Create Tables**: Recria todas as tabelas na ordem correta
   - tenants
   - users
   - roles
   - user_roles
   - api_tokens
   - projects
   - project_members
   - work_items
   - work_item_history
   - work_item_approvals
   - work_item_links
   - **project_specifications** (NOVO)
   - **project_architectures** (NOVO)

3. **Seed Data**: Cria dados iniciais
   - 1 Tenant (Test Organization)
   - 3 Roles (admin, dev, po)
   - 3 Users (admin, dev, po)

---

## ⚠️ Avisos

- **TODOS OS DADOS SERÃO PERDIDOS**
- Projetos, requisitos, work items serão deletados
- Use apenas em desenvolvimento
- Faça backup se necessário

---

## 🐛 Troubleshooting

### Erro: "could not find table 'tenants'"

**Causa**: Ordem de criação de tabelas incorreta

**Solução**: Execute o reset
```bash
./scripts/recreate_db.sh
```

### Erro: "permission denied"

**Causa**: Script não tem permissão de execução

**Solução**: 
```bash
chmod +x scripts/recreate_db.sh
./scripts/recreate_db.sh
```

### Erro: "database does not exist"

**Causa**: Banco de dados não foi criado

**Solução**: Criar banco manualmente
```bash
psql -U postgres -c "CREATE DATABASE bsmart_alm;"
python scripts/reset_and_seed.py
```

---

## 📝 Depois do Reset

1. **Iniciar Backend**
   ```bash
   cd services
   uvicorn api_gateway.main:app --reload --port 8086
   ```

2. **Iniciar Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Fazer Login**
   - Email: admin@example.com
   - Senha: admin123

4. **Criar Projeto de Teste**
   - Nome: "E-commerce Platform"
   - Target Cloud: AWS
   - MPS.BR Level: G

5. **Gerar Requisitos**
   - Usar modo Texto/Upload/URL
   - Aprovar requisitos

6. **Gerar Especificação**
   - Clicar em "Gerar Especificação"
   - Ver documento gerado

7. **Gerar Arquitetura**
   - Clicar em "Gerar Arquitetura"
   - Ver diagramas e requisitos não-funcionais

---

## ✅ Verificar Se Funcionou

Após o reset, o backend deve iniciar sem erros:

```
🚀 Starting Bsmart-ALM API Gateway...
✅ Database initialized
INFO: Application startup complete
INFO: Uvicorn running on http://127.0.0.1:8086
```

Se ver isso, está tudo OK! ✅

---

## 🎯 Quando Usar

Use o reset quando:
- ✅ Adicionar novos models
- ✅ Mudar estrutura de tabelas
- ✅ Ter erros de foreign key
- ✅ Quiser começar do zero
- ✅ Ambiente de desenvolvimento

**NÃO use em produção!** ⚠️

---

## 📊 Estrutura Final do Banco

Após o reset, você terá:

```
bsmart_alm (database)
├── tenants (1 registro)
├── users (3 registros)
├── roles (3 registros)
├── user_roles (0 registros)
├── api_tokens (0 registros)
├── projects (0 registros)
├── project_members (0 registros)
├── work_items (0 registros)
├── work_item_history (0 registros)
├── work_item_approvals (0 registros)
├── work_item_links (0 registros)
├── project_specifications (0 registros) ← NOVO
└── project_architectures (0 registros) ← NOVO
```

---

**Pronto para usar!** 🚀
