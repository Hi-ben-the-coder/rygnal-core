"""Approval lifecycle state transition enforcement."""

from dataclasses import dataclass, field

from rygnal.models import ApprovalStatus


@dataclass(frozen=True)
class ApprovalStateTransitionResult:
    """Structured result for approval state transition checks."""

    allowed: bool
    reason: str
    metadata: dict[str, str] = field(default_factory=dict)


class ApprovalStateMachine:
    """Validate approval lifecycle state transitions."""

    _ALLOWED_TRANSITIONS = frozenset(
        {
            (ApprovalStatus.PENDING, ApprovalStatus.APPROVED),
            (ApprovalStatus.PENDING, ApprovalStatus.REJECTED),
        }
    )

    @classmethod
    def validate_transition(
        cls,
        *,
        current_status: ApprovalStatus,
        next_status: ApprovalStatus,
    ) -> ApprovalStateTransitionResult:
        """Return whether an approval state transition is allowed."""
        if (current_status, next_status) in cls._ALLOWED_TRANSITIONS:
            return ApprovalStateTransitionResult(
                allowed=True,
                reason="Approval state transition allowed.",
                metadata={
                    "current_status": current_status.value,
                    "next_status": next_status.value,
                },
            )

        return ApprovalStateTransitionResult(
            allowed=False,
            reason=(
                f"Invalid approval state transition: {current_status.value} -> {next_status.value}."
            ),
            metadata={
                "guard": "approval-state-transition",
                "current_status": current_status.value,
                "next_status": next_status.value,
            },
        )
