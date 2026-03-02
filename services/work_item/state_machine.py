"""Work item state machine."""
from services.work_item.models import WorkItemStatus

# State transitions map
STATE_TRANSITIONS = {
    WorkItemStatus.DRAFT: [WorkItemStatus.IN_REVIEW],
    WorkItemStatus.IN_REVIEW: [WorkItemStatus.APPROVED, WorkItemStatus.REJECTED],
    WorkItemStatus.APPROVED: [WorkItemStatus.IN_PROGRESS],
    WorkItemStatus.REJECTED: [WorkItemStatus.DRAFT],
    WorkItemStatus.IN_PROGRESS: [WorkItemStatus.DONE],
    WorkItemStatus.DONE: [],  # Terminal state
}


def can_transition(current_status: WorkItemStatus, new_status: WorkItemStatus) -> bool:
    """Check if transition is valid."""
    allowed = STATE_TRANSITIONS.get(current_status, [])
    return new_status in allowed


def get_allowed_transitions(current_status: WorkItemStatus) -> list[WorkItemStatus]:
    """Get allowed transitions from current status."""
    return STATE_TRANSITIONS.get(current_status, [])
