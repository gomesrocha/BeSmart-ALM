import { ReactNode } from 'react'
import { usePermissions } from '../contexts/PermissionContext'

interface ProtectedProps {
  permission?: string
  anyPermission?: string[]
  allPermissions?: string[]
  role?: string
  fallback?: ReactNode
  children: ReactNode
}

export default function Protected({
  permission,
  anyPermission,
  allPermissions,
  role,
  fallback = null,
  children,
}: ProtectedProps) {
  const { hasPermission, hasAnyPermission, hasAllPermissions, hasRole, isLoading, permissions } = usePermissions()

  // While loading, don't show anything
  if (isLoading) {
    console.log('🔒 Protected: isLoading=true, hiding content')
    return null
  }

  // Check permission
  if (permission && !hasPermission(permission)) {
    console.log(`🔒 Protected: BLOCKED - missing permission "${permission}"`)
    console.log(`   Available permissions:`, permissions.slice(0, 5), '... (total:', permissions.length, ')')
    return <>{fallback}</>
  }

  // Check any permission
  if (anyPermission && !hasAnyPermission(anyPermission)) {
    console.log(`🔒 Protected: BLOCKED - missing any of permissions`, anyPermission)
    return <>{fallback}</>
  }

  // Check all permissions
  if (allPermissions && !hasAllPermissions(allPermissions)) {
    console.log(`🔒 Protected: BLOCKED - missing all permissions`, allPermissions)
    return <>{fallback}</>
  }

  // Check role
  if (role && !hasRole(role)) {
    console.log(`🔒 Protected: BLOCKED - missing role "${role}"`)
    return <>{fallback}</>
  }

  // User has permission, render children
  if (permission) {
    console.log(`✅ Protected: ALLOWED - has permission "${permission}"`)
  }
  return <>{children}</>
}
