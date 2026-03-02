"""Project router."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from sqlmodel import select

from services.identity.audit_service import AuditService
from services.identity.dependencies import (
    PermissionChecker,
    get_current_user,
    get_tenant_id,
)
from services.identity.models import User
from services.identity.permissions import Permission
from services.project.models import Project, ProjectMember, ProjectStatus
from services.project.schemas import (
    ProjectCreate,
    ProjectMemberAdd,
    ProjectMemberResponse,
    ProjectMemberUpdate,
    ProjectResponse,
    ProjectUpdate,
)
from services.shared.database import get_session

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_READ)),
    ],
    status: ProjectStatus | None = None,
) -> list[ProjectResponse]:
    """List all projects for tenant.

    Args:
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user
        status: Optional status filter

    Returns:
        List of projects
    """
    query = select(Project).where(Project.tenant_id == tenant_id)

    if status:
        query = query.where(Project.status == status)

    query = query.order_by(Project.created_at.desc())

    result = await session.execute(query)
    projects = result.scalars().all()
    return [ProjectResponse.model_validate(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_READ)),
    ],
) -> ProjectResponse:
    """Get project by ID.

    Args:
        project_id: Project ID
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        Project details

    Raises:
        HTTPException: If project not found
    """
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return ProjectResponse.model_validate(project)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_CREATE)),
    ],
) -> ProjectResponse:
    """Create new project.

    Args:
        project_data: Project creation data
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        Created project
    """
    # Create project
    project = Project(
        tenant_id=tenant_id,
        name=project_data.name,
        description=project_data.description,
        settings=project_data.settings.model_dump(),
        status=ProjectStatus.ACTIVE,
        created_by=current_user.id,
    )

    session.add(project)
    await session.commit()
    await session.refresh(project)

    # Add creator as owner
    member = ProjectMember(
        tenant_id=tenant_id,
        project_id=project.id,
        user_id=current_user.id,
        member_role="owner",
    )
    session.add(member)
    await session.commit()

    # Log audit
    await AuditService.log_action(
        session=session,
        tenant_id=tenant_id,
        user_id=current_user.id,
        action="project.create",
        resource_type="project",
        resource_id=project.id,
        details={"name": project.name, "status": project.status.value},
    )

    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_UPDATE)),
    ],
) -> ProjectResponse:
    """Update project.

    Args:
        project_id: Project ID
        project_data: Project update data
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        Updated project

    Raises:
        HTTPException: If project not found
    """
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Update fields
    updated_fields = []
    if project_data.name is not None:
        project.name = project_data.name
        updated_fields.append(f"name={project_data.name}")
    if project_data.description is not None:
        project.description = project_data.description
        updated_fields.append("description")
    if project_data.status is not None:
        project.status = project_data.status
        updated_fields.append(f"status={project_data.status}")
    if project_data.settings is not None:
        # Merge with existing settings
        current_settings = project.settings or {}
        current_settings.update(project_data.settings)
        project.settings = current_settings
        flag_modified(project, "settings")  # Marca como modificado para o SQLAlchemy
        updated_fields.append(f"settings={project_data.settings}")
    
    print(f"🔄 Updating project {project_id}: {', '.join(updated_fields)}")

    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    print(f"✅ Project updated successfully: {project.settings}")

    # Log audit
    await AuditService.log_action(
        session=session,
        tenant_id=tenant_id,
        user_id=current_user.id,
        action="project.update",
        resource_type="project",
        resource_id=project.id,
        details={"updated_fields": updated_fields},
    )

    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_DELETE)),
    ],
) -> None:
    """Delete project.

    Args:
        project_id: Project ID
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Raises:
        HTTPException: If project not found
    """
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Log audit before deletion
    await AuditService.log_action(
        session=session,
        tenant_id=tenant_id,
        user_id=current_user.id,
        action="project.delete",
        resource_type="project",
        resource_id=project.id,
        details={"name": project.name},
    )

    await session.delete(project)
    await session.commit()


@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
async def list_project_members(
    project_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_READ)),
    ],
) -> list[ProjectMemberResponse]:
    """List project members.

    Args:
        project_id: Project ID
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        List of project members

    Raises:
        HTTPException: If project not found
    """
    # Verify project exists
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Get members
    result = await session.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.tenant_id == tenant_id,
        )
    )
    members = result.scalars().all()

    return [ProjectMemberResponse.model_validate(member) for member in members]


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_member(
    project_id: UUID,
    member_data: ProjectMemberAdd,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_MANAGE_MEMBERS)),
    ],
) -> ProjectMemberResponse:
    """Add member to project.

    Args:
        project_id: Project ID
        member_data: Member data
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        Created project member

    Raises:
        HTTPException: If project not found or member already exists
    """
    # Verify project exists
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check if member already exists
    result = await session.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == member_data.user_id,
            ProjectMember.tenant_id == tenant_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this project",
        )

    # Add member
    member = ProjectMember(
        tenant_id=tenant_id,
        project_id=project_id,
        user_id=member_data.user_id,
        role_id=member_data.role_id,
        member_role=member_data.member_role,
    )

    session.add(member)
    await session.commit()
    await session.refresh(member)

    return ProjectMemberResponse.model_validate(member)


@router.delete(
    "/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_MANAGE_MEMBERS)),
    ],
) -> None:
    """Remove member from project.

    Args:
        project_id: Project ID
        user_id: User ID to remove
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Raises:
        HTTPException: If member not found
    """
    result = await session.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.tenant_id == tenant_id,
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    await session.delete(member)
    await session.commit()



# Project settings endpoints
@router.get("/{project_id}/settings", response_model=dict)
async def get_project_settings(
    project_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_READ)),
    ],
) -> dict:
    """Get project settings.

    Args:
        project_id: Project ID
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        Project settings

    Raises:
        HTTPException: If project not found
    """
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project.settings


@router.patch("/{project_id}/settings", response_model=dict)
async def update_project_settings(
    project_id: UUID,
    settings_data: dict,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_UPDATE)),
    ],
) -> dict:
    """Update project settings.

    Args:
        project_id: Project ID
        settings_data: Settings update data
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        Updated project settings

    Raises:
        HTTPException: If project not found
    """
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Merge settings
    current_settings = project.settings or {}
    current_settings.update(settings_data)
    project.settings = current_settings

    session.add(project)
    await session.commit()
    await session.refresh(project)

    return project.settings


@router.get("/{project_id}/whitelist", response_model=list[str])
async def get_project_whitelist(
    project_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_READ)),
    ],
) -> list[str]:
    """Get project URL whitelist.

    Args:
        project_id: Project ID
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        List of whitelisted URLs

    Raises:
        HTTPException: If project not found
    """
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project.settings.get("allowed_sources", [])


@router.post("/{project_id}/whitelist", response_model=list[str])
async def add_to_whitelist(
    project_id: UUID,
    url: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_UPDATE)),
    ],
) -> list[str]:
    """Add URL to project whitelist.

    Args:
        project_id: Project ID
        url: URL to add
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        Updated whitelist

    Raises:
        HTTPException: If project not found
    """
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Get current whitelist
    settings = project.settings or {}
    whitelist = settings.get("allowed_sources", [])

    # Add URL if not already present
    if url not in whitelist:
        whitelist.append(url)
        settings["allowed_sources"] = whitelist
        project.settings = settings

        session.add(project)
        await session.commit()

    return whitelist


@router.delete("/{project_id}/whitelist", response_model=list[str])
async def remove_from_whitelist(
    project_id: UUID,
    url: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.PROJECT_UPDATE)),
    ],
) -> list[str]:
    """Remove URL from project whitelist.

    Args:
        project_id: Project ID
        url: URL to remove
        session: Database session
        tenant_id: Tenant ID
        current_user: Current authenticated user

    Returns:
        Updated whitelist

    Raises:
        HTTPException: If project not found
    """
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Get current whitelist
    settings = project.settings or {}
    whitelist = settings.get("allowed_sources", [])

    # Remove URL if present
    if url in whitelist:
        whitelist.remove(url)
        settings["allowed_sources"] = whitelist
        project.settings = settings

        session.add(project)
        await session.commit()

    return whitelist
