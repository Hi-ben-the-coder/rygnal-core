"""Approval decision authorization for Rygnal.

This module validates whether an approval decision is allowed to take effect.
It supports both identity-level reviewer permissions and role permissions loaded
from operator-managed roles.yaml.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field

from rygnal.approval_state import ApprovalStateMachine
from rygnal.models import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
    RolePermission,
)


@dataclass(frozen=True)
class ApprovalReviewerPermission:
    """Permission assigned to a reviewer identity for approval decisions."""

    role: str
    can_approve: bool


@dataclass(frozen=True)
class ApprovalAuthorizationResult:
    """Structured result for approval authorization checks."""

    allowed: bool
    reason: str
    metadata: dict[str, str] = field(default_factory=dict)


class ApprovalAuthorizationEngine:
    """Authorize approval decisions before they affect tool execution."""

    def __init__(
        self,
        reviewer_permissions: Mapping[str, ApprovalReviewerPermission] | None = None,
        role_permissions: Mapping[str, RolePermission] | None = None,
    ) -> None:
        self.reviewer_permissions = dict(reviewer_permissions or {})
        self.role_permissions = dict(role_permissions or {})

    def authorize(
        self,
        *,
        approval_request: ApprovalRequest,
        approval_decision: ApprovalDecision,
        current_status: ApprovalStatus = ApprovalStatus.PENDING,
    ) -> ApprovalAuthorizationResult:
        """Return whether an approval decision is authorized."""
        transition_result = ApprovalStateMachine.validate_transition(
            current_status=current_status,
            next_status=approval_decision.status,
        )
        if not transition_result.allowed:
            return ApprovalAuthorizationResult(
                allowed=False,
                reason=transition_result.reason,
                metadata=transition_result.metadata,
            )

        if approval_decision.status == ApprovalStatus.REJECTED:
            return ApprovalAuthorizationResult(
                allowed=True,
                reason="Approval rejection authorized.",
                metadata={},
            )

        if approval_decision.decided_by is None:
            return ApprovalAuthorizationResult(
                allowed=False,
                reason="Approval decision is missing reviewer identity.",
                metadata={"guard": "reviewer-identity"},
            )

        if approval_decision.decided_by == approval_request.requested_by:
            return ApprovalAuthorizationResult(
                allowed=False,
                reason="Requester cannot approve their own approval request.",
                metadata={
                    "guard": "self-approval",
                    "attempted_decided_by": approval_decision.decided_by,
                },
            )

        role_result = self._authorize_role_permission(
            approval_request=approval_request,
            approval_decision=approval_decision,
        )
        if role_result is not None:
            return role_result

        reviewer_result = self._authorize_reviewer_permission(approval_decision)
        if reviewer_result is not None:
            return reviewer_result

        return ApprovalAuthorizationResult(
            allowed=True,
            reason="Approval decision authorized.",
            metadata={},
        )

    def _authorize_reviewer_permission(
        self,
        approval_decision: ApprovalDecision,
    ) -> ApprovalAuthorizationResult | None:
        reviewer_permission = self.reviewer_permissions.get(approval_decision.decided_by)

        if reviewer_permission is None:
            if self.reviewer_permissions:
                return ApprovalAuthorizationResult(
                    allowed=False,
                    reason="Reviewer does not have approval permission.",
                    metadata={
                        "guard": "reviewer-role",
                        "attempted_decided_by": approval_decision.decided_by or "",
                    },
                )

            return None

        reviewer_role = reviewer_permission.role.strip().lower()

        if not reviewer_permission.can_approve:
            return ApprovalAuthorizationResult(
                allowed=False,
                reason=(
                    f"Reviewer role '{reviewer_permission.role}' cannot approve protected actions."
                ),
                metadata={
                    "guard": "reviewer-role",
                    "attempted_decided_by": approval_decision.decided_by or "",
                    "reviewer_role": reviewer_role,
                },
            )

        return ApprovalAuthorizationResult(
            allowed=True,
            reason="Approval decision authorized.",
            metadata={"reviewer_role": reviewer_role},
        )

    def _authorize_role_permission(
        self,
        *,
        approval_request: ApprovalRequest,
        approval_decision: ApprovalDecision,
    ) -> ApprovalAuthorizationResult | None:
        if not self.role_permissions:
            return None

        reviewer_role = approval_decision.metadata.get("reviewer_role")
        if not isinstance(reviewer_role, str) or not reviewer_role.strip():
            return ApprovalAuthorizationResult(
                allowed=False,
                reason="Approval decision is missing reviewer role.",
                metadata={
                    "guard": "role-permission",
                    "attempted_decided_by": approval_decision.decided_by or "",
                    "denied_constraint": "reviewer_role",
                },
            )

        normalized_role = reviewer_role.strip().lower()
        role_permission = self.role_permissions.get(normalized_role)

        if role_permission is None:
            return ApprovalAuthorizationResult(
                allowed=False,
                reason=f"Reviewer role '{reviewer_role}' is not configured.",
                metadata={
                    "guard": "role-permission",
                    "attempted_decided_by": approval_decision.decided_by or "",
                    "reviewer_role": normalized_role,
                    "denied_constraint": "reviewer_role",
                },
            )

        return _authorize_role_constraints(
            approval_request=approval_request,
            approval_decision=approval_decision,
            reviewer_role=normalized_role,
            role_permission=role_permission,
        )


def _authorize_role_constraints(
    *,
    approval_request: ApprovalRequest,
    approval_decision: ApprovalDecision,
    reviewer_role: str,
    role_permission: RolePermission,
) -> ApprovalAuthorizationResult:
    base_metadata = {
        "reviewer_role": reviewer_role,
        "attempted_decided_by": approval_decision.decided_by or "",
    }

    if approval_request.severity not in role_permission.allowed_severities:
        return _deny_role_permission(
            reviewer_role=reviewer_role,
            denied_constraint="severity",
            metadata=base_metadata,
        )

    if (
        role_permission.allowed_actions is not None
        and approval_request.action not in role_permission.allowed_actions
    ):
        return _deny_role_permission(
            reviewer_role=reviewer_role,
            denied_constraint="action",
            metadata=base_metadata,
        )

    if (
        role_permission.environments is not None
        and approval_request.environment not in role_permission.environments
    ):
        return _deny_role_permission(
            reviewer_role=reviewer_role,
            denied_constraint="environment",
            metadata=base_metadata,
        )

    return ApprovalAuthorizationResult(
        allowed=True,
        reason="Approval decision authorized.",
        metadata=base_metadata,
    )


def _deny_role_permission(
    *,
    reviewer_role: str,
    denied_constraint: str,
    metadata: dict[str, str],
) -> ApprovalAuthorizationResult:
    return ApprovalAuthorizationResult(
        allowed=False,
        reason=(
            f"Reviewer role '{reviewer_role}' is not permitted to approve this {denied_constraint}."
        ),
        metadata={
            **metadata,
            "guard": "role-permission",
            "denied_constraint": denied_constraint,
        },
    )
