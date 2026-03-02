import { Link, useLocation } from 'react-router-dom'
import { Home, FolderKanban, ListTodo, Users, BarChart3, Building2, Shield } from 'lucide-react'
import { clsx } from 'clsx'
import { useAuthStore } from '../stores/authStore'
import { usePermissions } from '../contexts/PermissionContext'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Work Items', href: '/work-items', icon: ListTodo },
  { name: 'Users', href: '/users', icon: Users },
  { name: 'AI Stats', href: '/ai-stats', icon: BarChart3 },
]

const superAdminNavigation = [
  { name: 'Tenants', href: '/tenants', icon: Building2 },
]

const tenantAdminNavigation = [
  { name: 'User Roles', href: '/user-roles', icon: Shield },
]

export default function Sidebar() {
  const location = useLocation()
  const user = useAuthStore(state => state.user)
  const { hasRole, hasPermission, isSuperAdmin: isSuperAdminFromPermissions, roles } = usePermissions()
  
  // Super admins see everything
  const isSuperAdmin = user?.is_superuser === true || isSuperAdminFromPermissions
  
  // Tenant admins have Admin or Tenant Admin role OR have user management permissions
  // TEMPORÁRIO: Usar permissões ao invés de roles porque backend não retorna roles corretamente
  const isTenantAdmin = hasRole('Admin') || hasRole('Tenant Admin') || 
                        hasPermission('user:role:read') || hasPermission('user:role:assign')
  
  // Debug log
  console.log('🔍 Sidebar visibility:', {
    user_email: user?.email,
    is_superuser: user?.is_superuser,
    isSuperAdmin,
    isTenantAdmin,
    roles: roles.map(r => r.name),
    has_user_role_read: hasPermission('user:role:read'),
    has_user_role_assign: hasPermission('user:role:assign'),
    showUserRoles: isSuperAdmin || isTenantAdmin
  })
  
  // Show User Roles for super admins and tenant admins ONLY
  const showUserRoles = isSuperAdmin || isTenantAdmin

  return (
    <div className="w-64 bg-white border-r border-gray-200">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-primary-600">🐝 BeSmart-ALM</h1>
        <p className="text-sm text-gray-500 mt-1">AI-First ALM</p>
      </div>
      <nav className="px-3 space-y-1">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={clsx(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-50'
              )}
            >
              <Icon className="w-5 h-5" />
              {item.name}
            </Link>
          )
        })}
        
        {/* Admin Section */}
        {(isSuperAdmin || showUserRoles) && (
          <>
            <div className="pt-4 pb-2 px-3">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Administration
              </p>
            </div>
            
            {/* Super Admin Only: Tenants */}
            {isSuperAdmin && superAdminNavigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-50'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  {item.name}
                </Link>
              )
            })}
            
            {/* Tenant Admin & Super Admin: User Roles */}
            {showUserRoles && tenantAdminNavigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-50'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  {item.name}
                </Link>
              )
            })}
          </>
        )}
      </nav>
    </div>
  )
}
