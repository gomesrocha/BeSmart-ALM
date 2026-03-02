"""Permission definitions and RBAC utilities."""
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from services.identity.models import Role, User, UserRole


class Permission(str, Enum):
    """System permissions."""

    # Project permissions
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_MANAGE_MEMBERS = "project:manage_members"

    # Work item permissions
    WORK_ITEM_CREATE = "work_item:create"
    WORK_ITEM_READ = "work_item:read"
    WORK_ITEM_UPDATE = "work_item:update"
    WORK_ITEM_DELETE = "work_item:delete"
    WORK_ITEM_APPROVE = "work_item:approve"
    WORK_ITEM_TRANSITION = "work_item:transition"

    # Requirements permissions
    REQUIREMENTS_CREATE = "requirements:create"
    REQUIREMENTS_READ = "requirements:read"
    REQUIREMENTS_UPDATE = "requirements:update"
    REQUIREMENTS_DELETE = "requirements:delete"
    REQUIREMENTS_APPROVE = "requirements:approve"

    # Code permissions
    CODE_GENERATE = "code:generate"
    CODE_REVIEW = "code:review"
    CODE_COMMIT = "code:commit"

    # Testing permissions
    TESTING_CREATE = "testing:create"
    TESTING_EXECUTE = "testing:execute"
    TESTING_VIEW = "testing:view"

    # Security permissions
    SECURITY_SCAN = "security:scan"
    SECURITY_TRIAGE = "security:triage"
    SECURITY_VIEW = "security:view"

    # Management permissions
    MANAGEMENT_VIEW_DASHBOARD = "management:view_dashboard"
    MANAGEMENT_VIEW_METRICS = "management:view_metrics"
    MANAGEMENT_EXPORT_REPORTS = "management:export_reports"

    # Admin permissions
    ADMIN_MANAGE_USERS = "admin:manage_users"
    ADMIN_MANAGE_ROLES = "admin:manage_roles"
    ADMIN_MANAGE_SETTINGS = "admin:manage_settings"
    ADMIN_VIEW_AUDIT = "admin:view_audit"
    
    # Audit permissions
    AUDIT_VIEW = "audit:view"


# Default role permissions
DEFAULT_ROLE_PERMISSIONS = {
    "admin": [
        # All permissions
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
        Permission.PROJECT_MANAGE_MEMBERS,
        Permission.WORK_ITEM_CREATE,
        Permission.WORK_ITEM_READ,
        Permission.WORK_ITEM_UPDATE,
        Permission.WORK_ITEM_DELETE,
        Permission.WORK_ITEM_APPROVE,
        Permission.WORK_ITEM_TRANSITION,
        Permission.REQUIREMENTS_CREATE,
        Permission.REQUIREMENTS_READ,
        Permission.REQUIREMENTS_UPDATE,
        Permission.REQUIREMENTS_DELETE,
        Permission.REQUIREMENTS_APPROVE,
        Permission.CODE_GENERATE,
        Permission.CODE_REVIEW,
        Permission.CODE_COMMIT,
        Permission.TESTING_CREATE,
        Permission.TESTING_EXECUTE,
        Permission.TESTING_VIEW,
        Permission.SECURITY_SCAN,
        Permission.SECURITY_TRIAGE,
        Permission.SECURITY_VIEW,
        Permission.MANAGEMENT_VIEW_DASHBOARD,
        Permission.MANAGEMENT_VIEW_METRICS,
        Permission.MANAGEMENT_EXPORT_REPORTS,
        Permission.ADMIN_MANAGE_USERS,
        Permission.ADMIN_MANAGE_ROLES,
        Permission.ADMIN_MANAGE_SETTINGS,
        Permission.ADMIN_VIEW_AUDIT,
        Permission.AUDIT_VIEW,
    ],
    "po": [
        # Product Owner permissions
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.WORK_ITEM_CREATE,
        Permission.WORK_ITEM_READ,
        Permission.WORK_ITEM_UPDATE,
        Permission.WORK_ITEM_APPROVE,
        Permission.WORK_ITEM_TRANSITION,
        Permission.REQUIREMENTS_CREATE,
        Permission.REQUIREMENTS_READ,
        Permission.REQUIREMENTS_UPDATE,
        Permission.REQUIREMENTS_APPROVE,
        Permission.MANAGEMENT_VIEW_DASHBOARD,
        Permission.MANAGEMENT_VIEW_METRICS,
    ],
    "dev": [
        # Developer permissions
        Permission.PROJECT_READ,
        Permission.WORK_ITEM_READ,
        Permission.WORK_ITEM_UPDATE,
        Permission.WORK_ITEM_TRANSITION,
        Permission.REQUIREMENTS_READ,
        Permission.CODE_GENERATE,
        Permission.CODE_REVIEW,
        Permission.CODE_COMMIT,
        Permission.TESTING_CREATE,
        Permission.TESTING_EXECUTE,
        Permission.TESTING_VIEW,
        Permission.SECURITY_VIEW,
    ],
    "qa": [
        # QA Engineer permissions
        Permission.PROJECT_READ,
        Permission.WORK_ITEM_READ,
        Permission.WORK_ITEM_UPDATE,
        Permission.REQUIREMENTS_READ,
        Permission.CODE_REVIEW,
        Permission.TESTING_CREATE,
        Permission.TESTING_EXECUTE,
        Permission.TESTING_VIEW,
        Permission.SECURITY_VIEW,
        Permission.MANAGEMENT_VIEW_DASHBOARD,
    ],
    "sec": [
        # Security Engineer permissions
        Permission.PROJECT_READ,
        Permission.WORK_ITEM_READ,
        Permission.REQUIREMENTS_READ,
        Permission.CODE_REVIEW,
        Permission.SECURITY_SCAN,
        Permission.SECURITY_TRIAGE,
        Permission.SECURITY_VIEW,
        Permission.MANAGEMENT_VIEW_DASHBOARD,
    ],
    "auditor": [
        # Auditor permissions (read-only)
        Permission.PROJECT_READ,
        Permission.WORK_ITEM_READ,
        Permission.REQUIREMENTS_READ,
        Permission.TESTING_VIEW,
        Permission.SECURITY_VIEW,
        Permission.MANAGEMENT_VIEW_DASHBOARD,
        Permission.MANAGEMENT_VIEW_METRICS,
        Permission.MANAGEMENT_EXPORT_REPORTS,
        Permission.ADMIN_VIEW_AUDIT,
        Permission.AUDIT_VIEW,
    ],
}


async def get_user_permissions(
    user: User,
    session: AsyncSession,
    project_id: Optional[UUID] = None,
) -> set[str]:
    """Get all permissions for a user.

    Args:
        user: User to get permissions for
        session: Database session
        project_id: Optional project ID to filter project-specific roles

    Returns:
        Set of permission strings
    """
    # Superusers have all permissions
    if user.is_superuser:
        return {perm.value for perm in Permission}

    # Build query for user roles
    query = (
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user.id)
    )

    # Filter by project if specified
    if project_id:
        query = query.where(
            (UserRole.project_id == project_id) | (UserRole.project_id.is_(None))
        )

    result = await session.execute(query)
    roles = result.scalars().all()

    # Collect all permissions from roles
    permissions: set[str] = set()
    for role in roles:
        permissions.update(role.permissions)

    return permissions


async def check_permission(
    user: User,
    permission: Permission | str,
    session: AsyncSession,
    project_id: Optional[UUID] = None,
) -> bool:
    """Check if user has a specific permission.

    Args:
        user: User to check
        permission: Permission to check
        session: Database session
        project_id: Optional project ID for project-specific permissions

    Returns:
        True if user has permission, False otherwise
    """
    if isinstance(permission, Permission):
        permission = permission.value

    user_permissions = await get_user_permissions(user, session, project_id)
    return permission in user_permissions


async def require_permission(
    user: User,
    permission: Permission | str,
    session: AsyncSession,
    project_id: Optional[UUID] = None,
) -> None:
    """Require user to have a specific permission.

    Args:
        user: User to check
        permission: Permission to require
        session: Database session
        project_id: Optional project ID for project-specific permissions

    Raises:
        PermissionError: If user doesn't have permission
    """
    if not await check_permission(user, permission, session, project_id):
        raise PermissionError(f"User does not have permission: {permission}")


async def create_default_roles(tenant_id: UUID, session: AsyncSession) -> list[Role]:
    """Create default roles for a tenant.

    Args:
        tenant_id: Tenant ID
        session: Database session

    Returns:
        List of created roles
    """
    roles = []

    for role_name, permissions in DEFAULT_ROLE_PERMISSIONS.items():
        role = Role(
            tenant_id=tenant_id,
            name=role_name,
            description=f"Default {role_name} role",
            permissions=[p.value for p in permissions],
            is_system=True,
        )
        session.add(role)
        roles.append(role)

    await session.commit()
    return roles
