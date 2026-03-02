# 🧪 Guia de Teste - Frontend Bsmart-ALM

## 🚀 Início Rápido

### 1. Iniciar o Backend

```bash
# Terminal 1 - Backend
uv run uvicorn services.api_gateway.main:app --reload --port 8086
```

### 2. Iniciar o Frontend

```bash
# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Acessar a Aplicação

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8086
- **Swagger Docs**: http://localhost:8086/docs

## 🔐 Credenciais de Teste

Use as credenciais criadas pelo seed script:

```
Email: admin@test.com
Senha: admin123456
```

## ✅ Checklist de Testes

### 1. Autenticação

- [ ] Acessar http://localhost:3000
- [ ] Deve redirecionar para `/login`
- [ ] Inserir credenciais de teste
- [ ] Clicar em "Sign in"
- [ ] Deve redirecionar para o Dashboard
- [ ] Verificar nome do usuário no header
- [ ] Clicar no avatar e fazer logout
- [ ] Deve voltar para a tela de login

### 2. Dashboard

- [ ] Fazer login novamente
- [ ] Verificar cards de estatísticas:
  - Total Projects
  - Work Items
  - In Progress
  - Completed
- [ ] Verificar seção "Recent Projects"
- [ ] Verificar seção "Recent Work Items"
- [ ] Clicar em "View all" para Projects
- [ ] Clicar em "View all" para Work Items

### 3. Projects

- [ ] Navegar para "Projects" na sidebar
- [ ] Verificar lista de projetos existentes
- [ ] Clicar em "New Project"
- [ ] Preencher formulário:
  - Name: "Test Project"
  - Description: "This is a test project"
- [ ] Clicar em "Create Project"
- [ ] Verificar se o projeto aparece na lista
- [ ] Testar busca digitando no campo de pesquisa
- [ ] Clicar em um projeto para ver detalhes (placeholder)

### 4. Work Items

- [ ] Navegar para "Work Items" na sidebar
- [ ] Verificar lista de work items existentes
- [ ] Clicar em "New Work Item"
- [ ] Preencher formulário:
  - Title: "Test User Story"
  - Type: "User Story"
  - Project: Selecionar um projeto
  - Description: "As a user, I want to test the system"
- [ ] Clicar em "Create Work Item"
- [ ] Verificar se o work item aparece na lista
- [ ] Testar filtros:
  - Filtrar por Status
  - Filtrar por Type
  - Buscar por texto
- [ ] Verificar badges de status e tipo
- [ ] Clicar em um work item para ver detalhes (placeholder)

### 5. Navegação

- [ ] Testar navegação entre páginas usando a sidebar
- [ ] Verificar que a página ativa está destacada
- [ ] Testar navegação usando o browser (back/forward)
- [ ] Verificar que o estado é mantido

### 6. Responsividade

- [ ] Redimensionar a janela do browser
- [ ] Verificar layout em diferentes tamanhos:
  - Desktop (> 1024px)
  - Tablet (768px - 1024px)
  - Mobile (< 768px)
- [ ] Verificar que os cards se reorganizam
- [ ] Verificar que os formulários são usáveis

### 7. Tratamento de Erros

- [ ] Fazer logout
- [ ] Tentar fazer login com credenciais inválidas
- [ ] Verificar mensagem de erro
- [ ] Fazer login com credenciais corretas
- [ ] Parar o backend
- [ ] Tentar criar um projeto
- [ ] Verificar que o erro é tratado
- [ ] Reiniciar o backend

## 🐛 Problemas Comuns

### Frontend não inicia

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend não conecta

Verificar se o backend está rodando:
```bash
curl http://localhost:8086/health
```

### Erro de CORS

O Vite está configurado para fazer proxy. Verificar `vite.config.ts`:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8086',
    changeOrigin: true,
  },
}
```

### Token expirado

Fazer logout e login novamente.

## 📊 Resultados Esperados

### Dashboard
- 4 cards de estatísticas com números corretos
- Lista de projetos recentes (até 5)
- Lista de work items recentes (até 5)

### Projects
- Grid responsivo de projetos
- Formulário de criação funcional
- Busca em tempo real
- Status badges coloridos

### Work Items
- Lista de work items com filtros
- Formulário de criação com validação
- Badges de status e tipo
- Busca e filtros funcionando

## 🎯 Próximos Passos

Após validar o frontend básico:

1. Implementar páginas de detalhes (ProjectDetail, WorkItemDetail)
2. Adicionar edição de projetos e work items
3. Implementar transições de estado para work items
4. Adicionar mais funcionalidades do backend
5. Implementar testes E2E com Playwright

## 📝 Notas

- O frontend está usando mock data do backend
- Algumas páginas são placeholders (Detail pages)
- O design é responsivo e segue o Tailwind CSS
- A autenticação usa JWT tokens
- O estado é gerenciado com Zustand

**Frontend completo e pronto para testes!** ✨
