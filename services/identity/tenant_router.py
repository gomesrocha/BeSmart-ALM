"""Tenant management router."""
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from services.identity.dependencies import get_current_user
from services.identity.decorators import require_super_admin
from services.identity.models import User, Role
from services.identity.tenant_service import TenantService
from services.identity.security import hash_password
from services.shared.database import get_session

router = APIRouter(prefix="/tenants", tags=["Tenants"])


# Schemas
class TenantCreate(BaseModel):
    """Schema for creating a tenant."""

    name: str
    slug: str
    is_active: bool = True


class TenantAdminCreate(BaseModel):
    """Schema for admin user when creating tenant."""

    email: str
    password: str
    full_name: str


class TenantWithAdminCreate(BaseModel):
    """Schema for creating a tenant with its admin user."""

    tenant: TenantCreate
    admin: TenantAdminCreate


class TenantUpdate(BaseModel):
    """Schema for updating a tenant."""

    name: Optional[str] = None
    is_active: Optional[bool] = None


class TenantResponse(BaseModel):
    """Schema for tenant response."""

    id: UUID
    name: str
    slug: str
    is_active: bool
    settings: dict = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
@require_super_admin()
async def create_tenant(
    tenant_data: TenantCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TenantResponse:
    """Create a new tenant (super admin only).

    Args:
        tenant_data: Tenant creation data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Created tenant

    Raises:
        HTTPException: If slug already exists
    """
    try:
        tenant = await TenantService.create_tenant(
            session=session,
            name=tenant_data.name,
            slug=tenant_data.slug,
        )

        return TenantResponse.model_validate(tenant)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post("/with-admin", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
@require_super_admin()
async def create_tenant_with_admin(
    data: TenantWithAdminCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TenantResponse:
    """Create a new tenant with its admin user (super admin only).

    This endpoint creates:
    1. A new tenant
    2. An admin user for that tenant
    3. Assigns the "Tenant Admin" role to the user
    4. Creates default roles for the tenant

    Args:
        data: Tenant and admin creation data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Created tenant

    Raises:
        HTTPException: If slug or email already exists
    """
    from sqlmodel import select
    from services.identity.models import UserRole
    from uuid import uuid4
    
    try:
        # 1. Create tenant
        tenant = await TenantService.create_tenant(
            session=session,
            name=data.tenant.name,
            slug=data.tenant.slug,
        )

        # 2. Check if email already exists
        result = await session.execute(
            select(User).where(User.email == data.admin.email)
        )
        if result.scalar_one_or_none():
            raise ValueError(f"Email '{data.admin.email}' already exists")

        # 3. Create admin user
        admin_user = User(
            id=uuid4(),
            tenant_id=tenant.id,
            email=data.admin.email,
            hashed_password=hash_password(data.admin.password),
            full_name=data.admin.full_name,
            is_active=True,
            is_superuser=False,
        )
        session.add(admin_user)
        await session.flush()

        # 4. Create default roles for tenant
        default_roles = [
            {
                "name": "Tenant Admin",
                "description": "Full access to tenant resources",
                "permissions": [
                    "user:create", "user:read", "user:update", "user:delete",
                    "role:create", "role:read", "role:update", "role:delete",
                    "project:create", "project:read", "project:update", "project:delete",
                    "workitem:create", "workitem:read", "workitem:update", "workitem:delete",
                ],
                "is_system": True,
            },
            {
                "name": "Project Manager",
                "description": "Manage projects and work items",
                "permissions": [
                    "project:create", "project:read", "project:update",
                    "workitem:create", "workitem:read", "workitem:update", "workitem:delete",
                ],
                "is_system": True,
            },
            {
                "name": "Developer",
                "description": "Work on assigned tasks",
                "permissions": [
                    "project:read",
                    "workitem:create", "workitem:read", "workitem:update",
                ],
                "is_system": False,
            },
            {
                "name": "Viewer",
                "description": "Read-only access",
                "permissions": [
                    "project:read",
                    "workitem:read",
                ],
                "is_system": False,
            },
        ]

        tenant_admin_role = None
        for role_data in default_roles:
            role = Role(
                id=uuid4(),
                tenant_id=tenant.id,
                name=role_data["name"],
                description=role_data["description"],
                permissions=role_data["permissions"],
                is_system=role_data["is_system"],
            )
            session.add(role)
            
            if role_data["name"] == "Tenant Admin":
                tenant_admin_role = role

        await session.flush()

        # 5. Assign Tenant Admin role to admin user
        if tenant_admin_role:
            user_role = UserRole(
                id=uuid4(),
                user_id=admin_user.id,
                role_id=tenant_admin_role.id,
            )
            session.add(user_role)

        await session.commit()
        await session.refresh(tenant)

        return TenantResponse.model_validate(tenant)

    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tenant: {str(e)}"
        )


@router.get("", response_model=list[TenantResponse])
@require_super_admin()
async def list_tenants(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    is_active: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[TenantResponse]:
    """List all tenants (super admin only).

    Args:
        session: Database session
        current_user: Current authenticated user
        is_active: Filter by active status (optional)
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        List of tenants
    """
    tenants = await TenantService.list_tenants(
        session=session, is_active=is_active, limit=limit, offset=offset
    )

    return [TenantResponse.model_validate(tenant) for tenant in tenants]


@router.get("/{tenant_id}", response_model=TenantResponse)
@require_super_admin()
async def get_tenant(
    tenant_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TenantResponse:
    """Get tenant by ID (super admin only).

    Args:
        tenant_id: Tenant ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Tenant details

    Raises:
        HTTPException: If tenant not found
    """
    tenant = await TenantService.get_tenant(session=session, tenant_id=tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )

    return TenantResponse.model_validate(tenant)


@router.patch("/{tenant_id}", response_model=TenantResponse)
@require_super_admin()
async def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TenantResponse:
    """Update tenant (super admin only).

    Args:
        tenant_id: Tenant ID
        tenant_data: Tenant update data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Updated tenant

    Raises:
        HTTPException: If tenant not found
    """
    tenant = await TenantService.update_tenant(
        session=session,
        tenant_id=tenant_id,
        name=tenant_data.name,
        is_active=tenant_data.is_active,
    )

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )

    return TenantResponse.model_validate(tenant)


@router.get("/{tenant_id}/stats", response_model=dict)
@require_super_admin()
async def get_tenant_stats(
    tenant_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Get tenant statistics (super admin only).

    Args:
        tenant_id: Tenant ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Tenant statistics

    Raises:
        HTTPException: If tenant not found
    """
    stats = await TenantService.get_tenant_stats(
        session=session, tenant_id=tenant_id
    )

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )

    return stats


@router.patch("/{tenant_id}/toggle-active", status_code=status.HTTP_200_OK)
@require_super_admin()
async def toggle_tenant_active(
    tenant_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TenantResponse:
    """Toggle tenant active status (super admin only).

    Args:
        tenant_id: Tenant ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Updated tenant

    Raises:
        HTTPException: If tenant not found
    """
    tenant = await TenantService.get_tenant(session=session, tenant_id=tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )
    
    # Toggle active status
    tenant = await TenantService.update_tenant(
        session=session,
        tenant_id=tenant_id,
        is_active=not tenant.is_active,
    )

    return TenantResponse.model_validate(tenant)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_super_admin()
async def delete_tenant_permanently(
    tenant_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Permanently delete tenant and all related data (super admin only).
    
    WARNING: This action cannot be undone! All tenant data will be deleted:
    - User Roles
    - API Tokens
    - Audit Logs
    - Work Items
    - Projects
    - Users
    - Roles
    - Tenant

    Args:
        tenant_id: Tenant ID
        session: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If tenant not found or is protected
    """
    from sqlmodel import select
    from services.identity.models import UserRole, AuditLog, APIToken
    
    tenant = await TenantService.get_tenant(session=session, tenant_id=tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )
    
    # Protect system tenant from deletion
    if tenant.slug == "system":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system tenant. This tenant is reserved for super administrators."
        )
    
    try:
        # Delete in order to respect foreign key constraints
        
        # 1. Delete user roles
        result = await session.execute(
            select(UserRole).join(User).where(User.tenant_id == tenant_id)
        )
        user_roles = result.scalars().all()
        for ur in user_roles:
            await session.delete(ur)
        
        # 2. Delete API tokens
        result = await session.execute(
            select(APIToken).where(APIToken.tenant_id == tenant_id)
        )
        tokens = result.scalars().all()
        for token in tokens:
            await session.delete(token)
        
        # 3. Delete audit logs
        result = await session.execute(
            select(AuditLog).where(AuditLog.tenant_id == tenant_id)
        )
        logs = result.scalars().all()
        for log in logs:
            await session.delete(log)
        
        # 4. Delete work item history and work items
        try:
            from services.work_item.models import WorkItem, WorkItemHistory
            
            # 4a. Delete work item history first
            result = await session.execute(
                select(WorkItemHistory)
                .join(WorkItem, WorkItemHistory.work_item_id == WorkItem.id)
                .where(WorkItem.tenant_id == tenant_id)
            )
            histories = result.scalars().all()
            for history in histories:
                await session.delete(history)
            
            # 4b. Delete work items
            result = await session.execute(
                select(WorkItem).where(WorkItem.tenant_id == tenant_id)
            )
            work_items = result.scalars().all()
            for wi in work_items:
                await session.delete(wi)
        except (ImportError, AttributeError):
            pass  # WorkItem models may not exist yet
        
        # 5. Delete project specifications, documents, members and projects
        try:
            from services.project.models import Project, ProjectMember
            from services.specification.models import ProjectSpecification, ProjectArchitecture
            from services.project.document_models import ProjectDocument
            
            # 5a. Delete project documents
            result = await session.execute(
                select(ProjectDocument)
                .join(Project, ProjectDocument.project_id == Project.id)
                .where(Project.tenant_id == tenant_id)
            )
            docs = result.scalars().all()
            for doc in docs:
                await session.delete(doc)
            
            # 5b. Delete project specifications and architecture
            result = await session.execute(
                select(ProjectSpecification)
                .join(Project, ProjectSpecification.project_id == Project.id)
                .where(Project.tenant_id == tenant_id)
            )
            specs = result.scalars().all()
            for spec in specs:
                await session.delete(spec)
            
            result = await session.execute(
                select(ProjectArchitecture)
                .join(Project, ProjectArchitecture.project_id == Project.id)
                .where(Project.tenant_id == tenant_id)
            )
            archs = result.scalars().all()
            for arch in archs:
                await session.delete(arch)
            
            # 5c. Delete project members
            result = await session.execute(
                select(ProjectMember)
                .join(Project, ProjectMember.project_id == Project.id)
                .where(Project.tenant_id == tenant_id)
            )
            members = result.scalars().all()
            for member in members:
                await session.delete(member)
            
            # 5d. Delete projects
            result = await session.execute(
                select(Project).where(Project.tenant_id == tenant_id)
            )
            projects = result.scalars().all()
            for project in projects:
                await session.delete(project)
        except (ImportError, AttributeError):
            pass  # Project models may not exist yet
        
        # 6. Delete users
        result = await session.execute(
            select(User).where(User.tenant_id == tenant_id)
        )
        users = result.scalars().all()
        for user in users:
            await session.delete(user)
        
        # 8. Delete roles
        result = await session.execute(
            select(Role).where(Role.tenant_id == tenant_id)
        )
        roles = result.scalars().all()
        for role in roles:
            await session.delete(role)
        
        # 9. Finally, delete tenant
        await session.delete(tenant)
        await session.commit()
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tenant: {str(e)}"
        )




@router.post("/{tenant_id}/impersonate")
@require_super_admin()
async def impersonate_tenant(
    tenant_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Allow super admin to impersonate a tenant (access as that tenant).

    This creates a temporary session where the super admin can access
    the tenant's data as if they were a user of that tenant.

    Args:
        tenant_id: Tenant ID to impersonate
        session: Database session
        current_user: Current authenticated user (must be super admin)

    Returns:
        Token for impersonated session

    Raises:
        HTTPException: If tenant not found
    """
    from services.identity.security import create_access_token
    
    # Verify tenant exists
    tenant = await TenantService.get_tenant(session=session, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )

    # Create a special token with tenant context
    token_data = {
        "sub": str(current_user.id),
        "email": current_user.email,
        "is_superuser": True,
        "impersonated_tenant_id": str(tenant_id),
        "impersonated_tenant_name": tenant.name,
    }
    
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "tenant_id": str(tenant_id),
        "tenant_name": tenant.name,
        "message": f"Now accessing as tenant: {tenant.name}",
    }
