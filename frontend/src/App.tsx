import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { PermissionProvider } from './contexts/PermissionContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import ProjectDocumentsPage from './pages/ProjectDocumentsPage'
import DocumentViewer from './pages/DocumentViewer'
import WorkItems from './pages/WorkItems'
import WorkItemsKanban from './pages/WorkItemsKanban'
import WorkItemDetail from './pages/WorkItemDetail'
import Users from './pages/Users'
import Tenants from './pages/Tenants'
import UserRoles from './pages/UserRoles'
import AIStats from './pages/AIStats'
import Layout from './components/Layout'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore(state => state.token)
  return token ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <PermissionProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
            <Route index element={<Dashboard />} />
            <Route path="projects" element={<Projects />} />
            <Route path="projects/:id" element={<ProjectDetail />} />
            <Route path="projects/:id/documents" element={<ProjectDocumentsPage />} />
            <Route path="projects/:projectId/documents/:documentId" element={<DocumentViewer />} />
            <Route path="work-items" element={<WorkItems />} />
            <Route path="work-items/kanban" element={<WorkItemsKanban />} />
            <Route path="work-items/:id" element={<WorkItemDetail />} />
            <Route path="users" element={<Users />} />
            <Route path="tenants" element={<Tenants />} />
            <Route path="user-roles" element={<UserRoles />} />
            <Route path="ai-stats" element={<AIStats />} />
            <Route path="projects/:projectId/ai-stats" element={<AIStats />} />
          </Route>
        </Routes>
      </PermissionProvider>
    </BrowserRouter>
  )
}

export default App
