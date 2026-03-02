# 🎨 Bsmart-ALM Frontend - Guia Completo

## ✅ Já Criado

- ✅ Configuração do projeto (package.json, vite, tailwind, typescript)
- ✅ Estrutura base

## 🚀 Como Instalar e Rodar

```bash
cd frontend
npm install
npm run dev
```

Acesse: http://localhost:3000

## 📁 Estrutura Completa a Criar

```
frontend/src/
├── App.tsx                    # App principal com rotas
├── main.tsx                   # Entry point
├── index.css                  # Estilos globais
├── api/
│   └── client.ts             # Axios client configurado
├── stores/
│   └── authStore.ts          # Zustand store para auth
├── types/
│   └── index.ts              # TypeScript types
├── pages/
│   ├── Login.tsx             # Página de login
│   ├── Dashboard.tsx         # Dashboard principal
│   ├── Projects.tsx          # Lista de projetos
│   ├── ProjectDetail.tsx     # Detalhes do projeto
│   ├── WorkItems.tsx         # Lista de work items
│   └── WorkItemDetail.tsx    # Detalhes do work item
└── components/
    ├── Layout.tsx            # Layout com sidebar
    ├── Sidebar.tsx           # Sidebar de navegação
    ├── Header.tsx            # Header com user menu
    ├── ProjectCard.tsx       # Card de projeto
    ├── WorkItemCard.tsx      # Card de work item
    └── StatusBadge.tsx       # Badge de status
```

## 🎯 Funcionalidades Principais

### 1. Autenticação
- Login com email/senha
- Armazenar token JWT
- Logout
- Proteção de rotas

### 2. Dashboard
- Resumo de projetos
- Work items recentes
- Estatísticas

### 3. Projetos
- Listar projetos
- Criar projeto
- Editar projeto
- Ver membros
- Configurações

### 4. Work Items
- Listar work items
- Criar work item
- Editar work item
- Transição de status
- Aprovar/Rejeitar
- Histórico

## 🎨 Design System

### Cores
- Primary: Blue (#0ea5e9)
- Success: Green
- Warning: Yellow
- Danger: Red
- Gray: Neutral

### Componentes
- Buttons: Primary, Secondary, Danger
- Cards: Shadow, Border
- Forms: Input, Select, Textarea
- Badges: Status colors
- Modals: Overlay + Card

## 📝 Exemplo de Implementação

### App.tsx
```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Layout from './components/Layout'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore(state => state.token)
  return token ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="projects" element={<Projects />} />
          <Route path="projects/:id" element={<ProjectDetail />} />
          <Route path="work-items" element={<WorkItems />} />
          <Route path="work-items/:id" element={<WorkItemDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

### api/client.ts
```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

### stores/authStore.ts
```typescript
import { create } from 'zustand'
import api from '../api/client'

interface AuthStore {
  token: string | null
  user: any | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  token: localStorage.getItem('token'),
  user: null,
  login: async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('token', data.access_token)
    set({ token: data.access_token })
  },
  logout: () => {
    localStorage.removeItem('token')
    set({ token: null, user: null })
  },
}))
```

## 🎨 Componentes de UI

### Button
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger'
  children: React.ReactNode
  onClick?: () => void
}

export function Button({ variant = 'primary', children, onClick }: ButtonProps) {
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>
      {children}
    </button>
  )
}
```

### Card
```typescript
export function Card({ children }: { children: React.ReactNode }) {
  return <div className="card">{children}</div>
}
```

## 📱 Páginas

### Login.tsx
- Form com email e senha
- Botão de login
- Mensagens de erro
- Redirect após login

### Dashboard.tsx
- Cards com estatísticas
- Lista de projetos recentes
- Lista de work items recentes
- Gráficos (opcional)

### Projects.tsx
- Lista de projetos em grid
- Botão "Novo Projeto"
- Filtros por status
- Search

### WorkItems.tsx
- Tabela de work items
- Filtros por tipo, status, projeto
- Botão "Novo Work Item"
- Kanban board (opcional)

## 🚀 Próximos Passos

1. Criar estrutura de pastas
2. Implementar API client
3. Criar auth store
4. Implementar páginas
5. Criar componentes
6. Adicionar rotas
7. Testar integração com backend

## 📚 Recursos

- React: https://react.dev
- Tailwind: https://tailwindcss.com
- React Router: https://reactrouter.com
- Zustand: https://github.com/pmndrs/zustand
- Lucide Icons: https://lucide.dev

## 🎉 Resultado Final

Um frontend moderno, responsivo e elegante que consome a API do Bsmart-ALM com:
- ✅ Autenticação JWT
- ✅ Gerenciamento de projetos
- ✅ Gerenciamento de work items
- ✅ Dashboard com estatísticas
- ✅ UI/UX profissional
- ✅ TypeScript para type safety
- ✅ Tailwind para design consistente
