"""Role management router."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from services.identity.dependencies import (
    PermissionChecker,
    get_current_user,
    get_tenant_id,
)
from services.identity.models import Role, User, UserRole
from services.identity.permissions import Permission
from services.identity.schemas import RoleCreate, RoleResponse, RoleUpdate
from services.shared.database import get_session

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=list[RoleResponse])
async def list_roles(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.ADMIN_MANAGE_ROLES)),
    ],
) -> list[RoleResponse]:
    """List all roles for tenant.

    Args:
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        List of roles
    """
    # Superusers can see roles from all tenants
    is_superuser = getattr(current_user, "is_superuser", False)
    
    if is_superuser:
        # Return roles from all tenants
        result = await session.execute(
            select(Role).order_by(Role.tenant_id, Role.name)
        )
    else:
        # Return only roles from current tenant
        result = await session.execute(
            select(Role).where(Role.tenant_id == tenant_id).order_by(Role.name)
        )
    
    roles = result.scalars().all()
    return [RoleResponse.model_validate(role) for role in roles]


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.ADMIN_MANAGE_ROLES)),
    ],
) -> RoleResponse:
    """Get role by ID.

    Args:
        role_id: Role ID
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        Role details

    Raises:
        HTTPException: If role not found
    """
    result = await session.execute(
        select(Role).where(Role.id == role_id, Role.tenant_id == tenant_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return RoleResponse.model_validate(role)


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.ADMIN_MANAGE_ROLES)),
    ],
) -> RoleResponse:
    """Create new role.

    Args:
        role_data: Role creation data
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        Created role

    Raises:
        HTTPException: If role name already exists
    """
    # Check if role name already exists
    result = await session.execute(
        select(Role).where(
            Role.tenant_id == tenant_id,
            Role.name == role_data.name,
        )
    )
    existing_role = result.scalar_one_or_none()

    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role with this name already exists",
        )

    # Create role
    role = Role(
        tenant_id=tenant_id,
        name=role_data.name,
        description=role_data.description,
        permissions=role_data.permissions,
        is_system=False,
    )

    session.add(role)
    await session.commit()
    await session.refresh(role)

    return RoleResponse.model_validate(role)


@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.ADMIN_MANAGE_ROLES)),
    ],
) -> RoleResponse:
    """Update role.

    Args:
        role_id: Role ID
        role_data: Role update data
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        Updated role

    Raises:
        HTTPException: If role not found or is system role
    """
    result = await session.execute(
        select(Role).where(Role.id == role_id, Role.tenant_id == tenant_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify system role",
        )

    # Update fields
    if role_data.name is not None:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description
    if role_data.permissions is not None:
        role.permissions = role_data.permissions

    session.add(role)
    await session.commit()
    await session.refresh(role)

    return RoleResponse.model_validate(role)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.ADMIN_MANAGE_ROLES)),
    ],
) -> None:
    """Delete role.

    Args:
        role_id: Role ID
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Raises:
        HTTPException: If role not found or is system role
    """
    result = await session.execute(
        select(Role).where(Role.id == role_id, Role.tenant_id == tenant_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system role",
        )

    # Check if role is assigned to any users
    result = await session.execute(select(UserRole).where(UserRole.role_id == role_id))
    user_roles = result.scalars().all()

    if user_roles:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete role that is assigned to users",
        )

    await session.delete(role)
    await session.commit()


@router.post("/{role_id}/assign/{user_id}", status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(
    role_id: UUID,
    user_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.ADMIN_MANAGE_USERS)),
    ],
    project_id: UUID | None = None,
) -> dict[str, str]:
    """Assign role to user.

    Args:
        role_id: Role ID
        user_id: User ID
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user
        project_id: Optional project ID for project-specific role

    Returns:
        Success message

    Raises:
        HTTPException: If role or user not found, or assignment already exists
    """
    # Verify role exists
    result = await session.execute(
        select(Role).where(Role.id == role_id, Role.tenant_id == tenant_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Verify user exists
    # Superusers can assign roles to users in any tenant
    is_superuser = getattr(current_user, "is_superuser", False)
    
    if is_superuser:
        # Superuser can assign to any user
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
    else:
        # Regular users can only assign to users in same tenant
        result = await session.execute(
            select(User).where(User.id == user_id, User.tenant_id == tenant_id)
        )
    
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if assignment already exists
    result = await session.execute(
        select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
            UserRole.project_id == project_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already assigned to user",
        )

    # Create assignment
    user_role = UserRole(
        user_id=user_id,
        role_id=role_id,
        project_id=project_id,
    )

    session.add(user_role)
    await session.commit()

    return {"message": "Role assigned successfully"}


@router.delete("/{role_id}/unassign/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_role_from_user(
    role_id: UUID,
    user_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.ADMIN_MANAGE_USERS)),
    ],
    project_id: UUID | None = None,
) -> None:
    """Unassign role from user.

    Args:
        role_id: Role ID
        user_id: User ID
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user
        project_id: Optional project ID for project-specific role

    Raises:
        HTTPException: If assignment not found
    """
    # Find assignment
    result = await session.execute(
        select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
            UserRole.project_id == project_id,
        )
    )
    user_role = result.scalar_one_or_none()

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found",
        )

    await session.delete(user_role)
    await session.commit()


@router.get("/user/{user_id}", response_model=list[dict])
async def get_user_roles(
    user_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(get_current_user)],
    project_id: UUID | None = None,
) -> list[dict]:
    """Get all roles assigned to a user.

    Args:
        user_id: User ID
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user
        project_id: Optional project ID to filter project-specific roles

    Returns:
        List of roles with assignment details

    Raises:
        HTTPException: If user not found or not authorized
    """
    # Verify user exists
    # Superusers can view roles for users in any tenant
    is_superuser = getattr(current_user, "is_superuser", False)
    
    if is_superuser:
        # Superuser can view any user's roles
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
    else:
        # Regular users can only view roles for users in same tenant
        result = await session.execute(
            select(User).where(User.id == user_id, User.tenant_id == tenant_id)
        )
    
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Only allow users to see their own roles or admins to see any
    if user_id != current_user.id and not is_superuser:
        # Check if current user has permission to manage users
        from services.identity.permission_service import PermissionService

        has_permission = await PermissionService.check_permission(
            user=current_user,
            permission="user.role.assign",
            session=session,
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view user roles",
            )

    # Get user roles
    from sqlalchemy.orm import selectinload

    query = select(UserRole).where(UserRole.user_id == user_id).options(
        selectinload(UserRole.role)
    )

    if project_id:
        query = query.where(UserRole.project_id == project_id)

    result = await session.execute(query)
    user_roles = result.scalars().all()

    # Format response
    roles_list = []
    for user_role in user_roles:
        if user_role.role:
            roles_list.append(
                {
                    "role_id": str(user_role.role_id),
                    "role_name": user_role.role.name,
                    "role_description": user_role.role.description,
                    "project_id": str(user_role.project_id)
                    if user_role.project_id
                    else None,
                    "assigned_at": user_role.created_at.isoformat()
                    if hasattr(user_role, "created_at")
                    else None,
                    "expires_at": user_role.expires_at.isoformat()
                    if hasattr(user_role, "expires_at") and user_role.expires_at
                    else None,
                }
            )

    return roles_list
