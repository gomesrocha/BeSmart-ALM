import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import api from '../api/client'

interface PermissionContextType {
  permissions: string[]
  roles: Role[]
  isLoading: boolean
  hasPermission: (permission: string) => boolean
  hasAnyPermission: (permissions: string[]) => boolean
  hasAllPermissions: (permissions: string[]) => boolean
  hasRole: (roleName: string) => boolean
  isSuperAdmin: boolean
  refetch: () => Promise<void>
}

interface Role {
  id: string
  name: string
  display_name: string
  description: string
}

export const PermissionContext = createContext<PermissionContextType | undefined>(undefined)

export function PermissionProvider({ children }: { children: ReactNode }) {
  const [permissions, setPermissions] = useState<string[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSuperAdmin, setIsSuperAdmin] = useState(false)

  const fetchPermissions = async () => {
    try {
      setIsLoading(true)
      console.log('🔄 Fetching permissions...')
      
      // Buscar user info
      const userResponse = await api.get('/auth/me')
      const userIsSuperAdmin = userResponse.data.is_superuser || false
      console.log('👤 User info:', { email: userResponse.data.email, is_superuser: userIsSuperAdmin })
      
      // Buscar permissões
      const { data } = await api.get('/auth/permissions')
      
      console.log('📋 Permissions API Response:', {
        is_super_admin: data.is_super_admin,
        permissions_count: (data.permissions || []).length,
        roles_count: (data.roles || []).length,
        roles: data.roles
      })
      
      // CORREÇÃO: Usar permissões reais do backend
      // Se for superadmin, backend retorna ["*"], caso contrário retorna array de permissões
      const backendPermissions = data.permissions || []
      
      console.log('📋 Setting permissions from backend:', backendPermissions.length, 'permissions')
      console.log('   First 5 permissions:', backendPermissions.slice(0, 5))
      setPermissions(backendPermissions)
      
      console.log('👥 Setting roles:', data.roles?.length || 0, 'roles')
      setRoles(data.roles || [])
      
      console.log('🔐 Setting isSuperAdmin:', userIsSuperAdmin)
      setIsSuperAdmin(userIsSuperAdmin)
      
      console.log('✅ Permissions granted:', {
        total: backendPermissions.length,
        has_project_create: backendPermissions.includes('project:create'),
        has_user_role_assign: backendPermissions.includes('user:role:assign'),
        has_work_item_transition: backendPermissions.includes('work_item:transition'),
        has_wildcard: backendPermissions.includes('*'),
        is_super_admin: userIsSuperAdmin,
        roles_count: (data.roles || []).length
      })
      
      // Verificar se realmente foi setado
      console.log('🔍 Verificação pós-set:')
      console.log('   permissions state será:', backendPermissions.length, 'items')
      console.log('   roles state será:', (data.roles || []).length, 'items')
      console.log('   isSuperAdmin state será:', userIsSuperAdmin)
      
      console.log('✅ Permissions loaded successfully')
    } catch (error) {
      console.error('❌ Failed to fetch permissions:', error)
      console.warn('⚠️ Using fallback permissions')
      setPermissions([
        'project:create', 'project:read', 'project:update', 'project:delete',
        'work_item:create', 'work_item:read', 'work_item:update',
        'user:read', 'user:write', 'user:delete',
        'user:role:assign', 'user:role:remove', 'user:role:read',
        'role:read', 'role:write', 'role:delete',
      ])
      setRoles([{ id: 'temp', name: 'Admin', display_name: 'Administrator', description: 'Fallback admin role' }])
      setIsSuperAdmin(false)
    } finally {
      setIsLoading(false)
      console.log('✅ Loading complete - isLoading set to FALSE')
    }
  }

  useEffect(() => {
    console.log('🔄 PermissionContext useEffect triggered')
    const token = localStorage.getItem('token')
    console.log('🔑 Token exists:', !!token)
    if (token) {
      console.log('✅ Token found, fetching permissions...')
      fetchPermissions()
    } else {
      console.log('❌ No token found, skipping permission fetch')
      setIsLoading(false)
    }
  }, [])

  const hasPermission = (permission: string): boolean => {
    // CRÍTICO: Verificar isSuperAdmin PRIMEIRO, antes de verificar array
    if (isSuperAdmin) {
      console.log(`✅ hasPermission("${permission}"): TRUE (superadmin)`)
      return true
    }
    
    // Verificar se tem wildcard "*" (superadmin via backend)
    if (permissions.includes('*')) {
      console.log(`✅ hasPermission("${permission}"): TRUE (wildcard *)`)
      return true
    }
    
    const result = permissions.includes(permission)
    console.log(`🔍 hasPermission("${permission}"): ${result} (permissions.length: ${permissions.length})`)
    return result
  }

  const hasAnyPermission = (perms: string[]): boolean => {
    if (isSuperAdmin) return true
    if (permissions.includes('*')) return true
    return perms.some(perm => permissions.includes(perm))
  }

  const hasAllPermissions = (perms: string[]): boolean => {
    if (isSuperAdmin) return true
    if (permissions.includes('*')) return true
    return perms.every(perm => permissions.includes(perm))
  }

  const hasRole = (roleName: string): boolean => {
    return roles.some(role => role.name === roleName)
  }

  const value: PermissionContextType = {
    permissions,
    roles,
    isLoading,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    isSuperAdmin,
    refetch: fetchPermissions,
  }

  return (
    <PermissionContext.Provider value={value}>
      {children}
    </PermissionContext.Provider>
  )
}

export function usePermissions() {
  const context = useContext(PermissionContext)
  if (context === undefined) {
    throw new Error('usePermissions must be used within a PermissionProvider')
  }
  return context
}
