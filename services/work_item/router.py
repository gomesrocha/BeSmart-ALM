"""Work item router."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from services.identity.audit_service import AuditService
from services.identity.dependencies import (
    PermissionChecker,
    get_current_user,
    get_tenant_id,
)
from services.identity.models import User
from services.identity.permissions import Permission
from services.work_item.models import WorkItem, WorkItemApproval, WorkItemHistory, WorkItemLink
from services.work_item.schemas import (
    WorkItemApprovalRequest,
    WorkItemCreate,
    WorkItemLinkCreate,
    WorkItemResponse,
    WorkItemStatusTransition,
    WorkItemUpdate,
)
from services.work_item.state_machine import can_transition
from services.shared.database import get_session

router = APIRouter(prefix="/work-items", tags=["Work Items"])


@router.get("", response_model=list[WorkItemResponse])
async def list_work_items(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.WORK_ITEM_READ))],
    project_id: UUID | None = None,
) -> list[WorkItemResponse]:
    """List work items."""
    query = select(WorkItem).where(WorkItem.tenant_id == tenant_id)
    if project_id:
        query = query.where(WorkItem.project_id == project_id)
    query = query.order_by(WorkItem.created_at.desc())
    result = await session.execute(query)
    items = result.scalars().all()
    return [WorkItemResponse.model_validate(item) for item in items]


@router.post("", response_model=WorkItemResponse, status_code=status.HTTP_201_CREATED)
async def create_work_item(
    item_data: WorkItemCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.WORK_ITEM_CREATE))],
) -> WorkItemResponse:
    """Create work item."""
    from services.work_item.models import WorkItemPriority
    
    item = WorkItem(
        tenant_id=tenant_id,
        project_id=item_data.project_id,
        type=item_data.type,
        title=item_data.title,
        description=item_data.description,
        priority=WorkItemPriority(item_data.priority) if item_data.priority else WorkItemPriority.MEDIUM,
        created_by=current_user.id,
        assigned_to=item_data.assigned_to,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return WorkItemResponse.model_validate(item)


@router.get("/{item_id}", response_model=WorkItemResponse)
async def get_work_item(
    item_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.WORK_ITEM_READ))],
) -> WorkItemResponse:
    """Get work item by ID."""
    result = await session.execute(
        select(WorkItem).where(WorkItem.id == item_id, WorkItem.tenant_id == tenant_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work item not found")
    return WorkItemResponse.model_validate(item)


@router.patch("/{item_id}", response_model=WorkItemResponse)
async def update_work_item(
    item_id: UUID,
    item_data: WorkItemUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.WORK_ITEM_UPDATE))],
) -> WorkItemResponse:
    """Update work item."""
    result = await session.execute(
        select(WorkItem).where(WorkItem.id == item_id, WorkItem.tenant_id == tenant_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work item not found")

    if item_data.title is not None:
        item.title = item_data.title
    if item_data.description is not None:
        item.description = item_data.description
    if item_data.priority is not None:
        item.priority = item_data.priority
    if item_data.assigned_to is not None:
        item.assigned_to = item_data.assigned_to

    session.add(item)
    await session.commit()
    await session.refresh(item)
    
    # Log audit
    updated_fields = []
    if item_data.title is not None:
        updated_fields.append("title")
    if item_data.description is not None:
        updated_fields.append("description")
    if item_data.priority is not None:
        updated_fields.append("priority")
    if item_data.assigned_to is not None:
        updated_fields.append("assigned_to")
    
    if updated_fields:
        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            user_id=current_user.id,
            action="workitem.update",
            resource_type="work_item",
            resource_id=item.id,
            details={"updated_fields": updated_fields},
        )
    
    return WorkItemResponse.model_validate(item)


@router.post("/{item_id}/transition", response_model=WorkItemResponse)
async def transition_status(
    item_id: UUID,
    transition: WorkItemStatusTransition,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.WORK_ITEM_TRANSITION))],
) -> WorkItemResponse:
    """Transition work item status."""
    result = await session.execute(
        select(WorkItem).where(WorkItem.id == item_id, WorkItem.tenant_id == tenant_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work item not found")

    if not can_transition(item.status, transition.new_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {item.status} to {transition.new_status}",
        )

    # Create history entry
    history = WorkItemHistory(
        tenant_id=tenant_id,
        work_item_id=item.id,
        version=item.version,
        changed_by=current_user.id,
        changes={"status": {"from": item.status, "to": transition.new_status}},
        snapshot={"title": item.title, "description": item.description, "status": item.status},
    )
    session.add(history)

    item.status = transition.new_status
    item.version += 1
    session.add(item)
    await session.commit()
    await session.refresh(item)
    
    # Log audit
    await AuditService.log_action(
        session=session,
        tenant_id=tenant_id,
        user_id=current_user.id,
        action="workitem.transition",
        resource_type="work_item",
        resource_id=item.id,
        details={"from_status": history.changes["status"]["from"], "to_status": transition.new_status},
    )
    
    return WorkItemResponse.model_validate(item)


@router.post("/{item_id}/approve")
async def approve_work_item(
    item_id: UUID,
    approval: WorkItemApprovalRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.WORK_ITEM_APPROVE))],
) -> dict[str, str]:
    """Approve or reject work item."""
    result = await session.execute(
        select(WorkItem).where(WorkItem.id == item_id, WorkItem.tenant_id == tenant_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work item not found")

    approval_record = WorkItemApproval(
        tenant_id=tenant_id,
        work_item_id=item.id,
        version=item.version,
        approved_by=current_user.id,
        decision=approval.decision,
        comments=approval.comments,
    )
    session.add(approval_record)
    await session.commit()
    return {"message": f"Work item {approval.decision.lower()}"}


@router.post("/{item_id}/links", status_code=status.HTTP_201_CREATED)
async def create_link(
    item_id: UUID,
    link_data: WorkItemLinkCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.WORK_ITEM_UPDATE))],
) -> dict[str, str]:
    """Create link between work items."""
    link = WorkItemLink(
        tenant_id=tenant_id,
        source_id=item_id,
        target_id=link_data.target_id,
        link_type=link_data.link_type,
    )
    session.add(link)
    await session.commit()
    return {"message": "Link created"}


@router.get("/{item_id}/comments", response_model=list)
async def list_comments(
    item_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.WORK_ITEM_READ))],
):
    """List work item comments."""
    from services.work_item.models import WorkItemComment
    from services.identity.models import User as UserModel
    
    query = (
        select(WorkItemComment, UserModel)
        .where(WorkItemComment.work_item_id == item_id)
        .where(WorkItemComment.tenant_id == tenant_id)
        .join(UserModel, WorkItemComment.created_by == UserModel.id)
        .order_by(WorkItemComment.created_at.asc())
    )
    result = await session.execute(query)
    comments_with_users = result.all()
    
    return [
        {
            "id": str(comment.id),
            "work_item_id": str(comment.work_item_id),
            "content": comment.content,
            "created_by": str(comment.created_by),
            "created_at": comment.created_at.isoformat(),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
            }
        }
        for comment, user in comments_with_users
    ]


@router.post("/{item_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    item_id: UUID,
    comment_data: dict,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.WORK_ITEM_READ))],
):
    """Create work item comment."""
    from services.work_item.models import WorkItemComment
    
    # Verify work item exists
    item = await session.get(WorkItem, item_id)
    if not item or item.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work item not found",
        )
    
    comment = WorkItemComment(
        tenant_id=tenant_id,
        work_item_id=item_id,
        content=comment_data["content"],
        created_by=current_user.id,
    )
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    
    return {
        "id": str(comment.id),
        "work_item_id": str(comment.work_item_id),
        "content": comment.content,
        "created_by": str(comment.created_by),
        "created_at": comment.created_at.isoformat(),
    }


@router.get("/{item_id}/transitions")
async def get_available_transitions(
    item_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.WORK_ITEM_READ))],
):
    """Get available status transitions for work item."""
    item = await session.get(WorkItem, item_id)
    if not item or item.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work item not found",
        )
    
    # Define available transitions based on current status
    transitions_map = {
        "draft": [
            {"to_state": "in_review", "label": "Submit for Review"},
        ],
        "in_review": [
            {"to_state": "approved", "label": "Approve"},
            {"to_state": "rejected", "label": "Reject"},
            {"to_state": "draft", "label": "Back to Draft"},
        ],
        "approved": [
            {"to_state": "in_progress", "label": "Start Work"},
        ],
        "rejected": [
            {"to_state": "draft", "label": "Revise"},
        ],
        "in_progress": [
            {"to_state": "done", "label": "Complete"},
            {"to_state": "approved", "label": "Back to Approved"},
        ],
        "done": [],
    }
    
    available = transitions_map.get(item.status.value, [])
    return {"transitions": available}


@router.post("/{item_id}/transition")
async def transition_work_item(
    item_id: UUID,
    transition_data: dict,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.WORK_ITEM_UPDATE))],
):
    """Transition work item to new status."""
    item = await session.get(WorkItem, item_id)
    if not item or item.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work item not found",
        )
    
    to_state = transition_data.get("to_state")
    if not to_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="to_state is required",
        )
    
    # Update status
    try:
        item.status = WorkItemStatus(to_state)
        await session.commit()
        await session.refresh(item)
        
        return {
            "id": str(item.id),
            "status": item.status.value,
            "message": f"Work item transitioned to {to_state}",
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {to_state}",
        )
