"""Approval workflow for Rygnal.

Approval Workflow v1 handles actions that require human approval before execution.
"""

from collections.abc import Callable
from typing import Any

from rygnal.models import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
    PolicyDecision,
    ToolRequest,
    utc_now_iso,
)

ApprovalResolver = Callable[[ApprovalRequest], ApprovalDecision]


class ApprovalWorkflow:
    """Create approval requests and resolve approve/reject decisions."""

    def __init__(self, resolver: ApprovalResolver | None = None) -> None:
        self.resolver = resolver or reject_by_default

    def request_approval(
        self,
        request: ToolRequest,
        policy_decision: PolicyDecision,
        risk_assessment: dict[str, Any] | None = None,
    ) -> tuple[ApprovalRequest, ApprovalDecision]:
        """Create an approval request and return the approval decision."""
        approval_request = ApprovalRequest(
            trace_id=str(request.metadata.get("trace_id") or ""),
            requested_by=request.user_id,
            agent_id=request.agent_id,
            environment=request.environment,
            tool_name=request.tool_name,
            action=request.action,
            target=request.target,
            policy_id=policy_decision.policy_id,
            reason=policy_decision.reason,
            risk_assessment=risk_assessment or {},
            metadata=request.metadata,
        )

        approval_decision = self.resolver(approval_request)

        if approval_decision.approval_id != approval_request.approval_id:
            raise ValueError("Approval decision ID does not match approval request ID.")

        return approval_request, approval_decision


def reject_by_default(approval_request: ApprovalRequest) -> ApprovalDecision:
    """Safe default resolver when no human approval system is configured."""
    return ApprovalDecision(
        approval_id=approval_request.approval_id,
        status=ApprovalStatus.REJECTED,
        approved=False,
        decided_by="system",
        decided_at=utc_now_iso(),
        reason="Approval workflow is not configured. Request rejected by default.",
    )


def approve_for_testing(
    approval_request: ApprovalRequest,
    decided_by: str = "test_reviewer",
    reason: str = "Approved for controlled test execution.",
) -> ApprovalDecision:
    """Approve an action for deterministic tests or controlled local workflows."""
    return ApprovalDecision(
        approval_id=approval_request.approval_id,
        status=ApprovalStatus.APPROVED,
        approved=True,
        decided_by=decided_by,
        decided_at=utc_now_iso(),
        reason=reason,
    )


def reject_for_testing(
    approval_request: ApprovalRequest,
    decided_by: str = "test_reviewer",
    reason: str = "Rejected for controlled test execution.",
) -> ApprovalDecision:
    """Reject an action for deterministic tests or controlled local workflows."""
    return ApprovalDecision(
        approval_id=approval_request.approval_id,
        status=ApprovalStatus.REJECTED,
        approved=False,
        decided_by=decided_by,
        decided_at=utc_now_iso(),
        reason=reason,
    )
