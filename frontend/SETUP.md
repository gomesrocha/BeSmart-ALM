# 🎨 Frontend Setup - Bsmart-ALM

## ✅ Implementação Completa

O frontend está 100% implementado com:

- ✅ **Login** com autenticação JWT
- ✅ **Dashboard** com estatísticas e resumos
- ✅ **Projects** - CRUD completo
- ✅ **Work Items** - CRUD completo
- ✅ **Layout** responsivo com sidebar e header
- ✅ **State Management** com Zustand
- ✅ **API Integration** com Axios
- ✅ **TypeScript** para type safety
- ✅ **Tailwind CSS** para design elegante

## 🚀 Como Rodar

```bash
# 1. Entrar na pasta frontend
cd frontend

# 2. Instalar dependências
npm install

# 3. Rodar em desenvolvimento
npm run dev
```

Acesse: **http://localhost:3000**

## 🔗 Integração com Backend

O frontend está configurado para se conectar com a API em `http://localhost:8086`.

Certifique-se de que o backend está rodando:

```bash
# Em outro terminal, na pasta raiz
uv run uvicorn services.api_gateway.main:app --reload --port 8086
```

## 🎯 Funcionalidades Implementadas

### 1. Autenticação
- Login com email/senha
- Logout
- Proteção de rotas
- Armazenamento de token JWT

### 2. Dashboard
- Estatísticas de projetos e work items
- Projetos recentes
- Work items recentes
- Cards com métricas

### 3. Projetos
- Listar todos os projetos
- Criar novo projeto
- Buscar projetos
- Cards com status e informações

### 4. Work Items
- Listar todos os work items
- Criar novo work item
- Filtrar por status e tipo
- Buscar work items
- Cards com badges de status

### 5. Layout
- Sidebar com navegação
- Header com menu do usuário
- Design responsivo
- Tema consistente

## 🎨 Design System

### Cores
- **Primary**: Blue (#0ea5e9)
- **Success**: Green
- **Warning**: Yellow
- **Danger**: Red

### Componentes
- **Buttons**: Primary, Secondary
- **Cards**: Shadow, Border, Hover effects
- **Forms**: Input, Select, Textarea
- **Badges**: Status colors
- **Layout**: Sidebar, Header, Main

## 📱 Páginas

1. **Login** (`/login`)
   - Form de autenticação
   - Credenciais de demo
   - Validação de campos

2. **Dashboard** (`/`)
   - Estatísticas gerais
   - Projetos recentes
   - Work items recentes

3. **Projects** (`/projects`)
   - Lista de projetos
   - Criar projeto
   - Buscar projetos

4. **Work Items** (`/work-items`)
   - Lista de work items
   - Criar work item
   - Filtros avançados

## 🔧 Tecnologias

- **React 18** - UI Library
- **TypeScript** - Type Safety
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **Zustand** - State Management
- **Axios** - HTTP Client
- **React Hook Form** - Forms
- **Lucide React** - Icons
- **Vite** - Build Tool

## 🎉 Resultado

Um frontend moderno, elegante e funcional que:

- ✅ Consome a API do Bsmart-ALM
- ✅ Tem design profissional
- ✅ É responsivo
- ✅ Tem type safety
- ✅ Gerencia estado eficientemente
- ✅ Tem navegação intuitiva
- ✅ Suporta todas as funcionalidades principais

**Pronto para uso!** 🚀
