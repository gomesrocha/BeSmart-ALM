"""Audit logs router."""
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from services.identity.audit_service import AuditService
from services.identity.dependencies import (
    PermissionChecker,
    get_current_user,
    get_tenant_id,
)
from services.identity.models import AuditLog, User
from services.identity.permissions import Permission
from services.shared.database import get_session

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("", response_model=dict)
async def list_audit_logs(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.AUDIT_VIEW)),
    ],
    user_id: UUID | None = Query(None, description="Filter by user ID"),
    action: str | None = Query(None, description="Filter by action"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    resource_id: UUID | None = Query(None, description="Filter by resource ID"),
    start_date: datetime | None = Query(None, description="Filter by start date"),
    end_date: datetime | None = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
) -> dict:
    """List audit logs with filters and pagination.
    
    Args:
        session: Database session
        tenant_id: Tenant ID (from middleware)
        current_user: Current authenticated user
        user_id: Optional user ID filter
        action: Optional action filter
        resource_type: Optional resource type filter
        resource_id: Optional resource ID filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        page: Page number (1-indexed)
        page_size: Items per page (max 100)
        
    Returns:
        Paginated audit logs with metadata
    """
    # Build base query
    query = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
    
    # Apply filters
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if resource_id:
        query = query.where(AuditLog.resource_id == resource_id)
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await session.execute(query)
    logs = result.scalars().all()
    
    # Calculate pagination metadata
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "items": [
            {
                "id": str(log.id),
                "tenant_id": str(log.tenant_id),
                "user_id": str(log.user_id),
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id) if log.resource_id else None,
                "details": log.details,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
        },
    }


@router.get("/actions", response_model=list[str])
async def list_audit_actions(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.AUDIT_VIEW)),
    ],
) -> list[str]:
    """List all unique actions in audit logs.
    
    Args:
        session: Database session
        tenant_id: Tenant ID (from middleware)
        current_user: Current authenticated user
        
    Returns:
        List of unique action names
    """
    query = (
        select(AuditLog.action)
        .where(AuditLog.tenant_id == tenant_id)
        .distinct()
        .order_by(AuditLog.action)
    )
    
    result = await session.execute(query)
    actions = result.scalars().all()
    
    return list(actions)


@router.get("/resource-types", response_model=list[str])
async def list_resource_types(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.AUDIT_VIEW)),
    ],
) -> list[str]:
    """List all unique resource types in audit logs.
    
    Args:
        session: Database session
        tenant_id: Tenant ID (from middleware)
        current_user: Current authenticated user
        
    Returns:
        List of unique resource types
    """
    query = (
        select(AuditLog.resource_type)
        .where(AuditLog.tenant_id == tenant_id)
        .distinct()
        .order_by(AuditLog.resource_type)
    )
    
    result = await session.execute(query)
    resource_types = result.scalars().all()
    
    return list(resource_types)


@router.get("/stats", response_model=dict)
async def get_audit_stats(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[
        User,
        Depends(PermissionChecker(Permission.AUDIT_VIEW)),
    ],
    start_date: datetime | None = Query(None, description="Start date for stats"),
    end_date: datetime | None = Query(None, description="End date for stats"),
) -> dict:
    """Get audit log statistics.
    
    Args:
        session: Database session
        tenant_id: Tenant ID (from middleware)
        current_user: Current authenticated user
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        Statistics about audit logs
    """
    # Build base query
    query = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
    
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()
    
    # Get count by action
    action_query = (
        select(AuditLog.action, func.count(AuditLog.id))
        .where(AuditLog.tenant_id == tenant_id)
        .group_by(AuditLog.action)
        .order_by(func.count(AuditLog.id).desc())
    )
    
    if start_date:
        action_query = action_query.where(AuditLog.created_at >= start_date)
    if end_date:
        action_query = action_query.where(AuditLog.created_at <= end_date)
    
    action_result = await session.execute(action_query)
    actions_by_count = [
        {"action": action, "count": count}
        for action, count in action_result.all()
    ]
    
    # Get count by resource type
    resource_query = (
        select(AuditLog.resource_type, func.count(AuditLog.id))
        .where(AuditLog.tenant_id == tenant_id)
        .group_by(AuditLog.resource_type)
        .order_by(func.count(AuditLog.id).desc())
    )
    
    if start_date:
        resource_query = resource_query.where(AuditLog.created_at >= start_date)
    if end_date:
        resource_query = resource_query.where(AuditLog.created_at <= end_date)
    
    resource_result = await session.execute(resource_query)
    resources_by_count = [
        {"resource_type": resource_type, "count": count}
        for resource_type, count in resource_result.all()
    ]
    
    # Get count by user
    user_query = (
        select(AuditLog.user_id, func.count(AuditLog.id))
        .where(AuditLog.tenant_id == tenant_id)
        .group_by(AuditLog.user_id)
        .order_by(func.count(AuditLog.id).desc())
        .limit(10)
    )
    
    if start_date:
        user_query = user_query.where(AuditLog.created_at >= start_date)
    if end_date:
        user_query = user_query.where(AuditLog.created_at <= end_date)
    
    user_result = await session.execute(user_query)
    users_by_count = [
        {"user_id": str(user_id), "count": count}
        for user_id, count in user_result.all()
    ]
    
    return {
        "total": total,
        "by_action": actions_by_count,
        "by_resource_type": resources_by_count,
        "top_users": users_by_count,
    }
