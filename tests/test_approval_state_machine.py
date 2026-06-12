from itertools import product

from rygnal.approval_authorization import ApprovalAuthorizationEngine
from rygnal.approval_state import ApprovalStateMachine
from rygnal.models import ApprovalDecision, ApprovalRequest, ApprovalStatus, utc_now_iso


def build_approval_request() -> ApprovalRequest:
    return ApprovalRequest(
        approval_id="approval_001",
        requested_by="requester",
        agent_id="demo_agent",
        environment="local",
        tool_name="file_delete",
        action="delete_file",
        target="customer-data.csv",
        reason="Sensitive file delete requires approval.",
    )


def build_approval_decision(status: ApprovalStatus) -> ApprovalDecision:
    return ApprovalDecision(
        approval_id="approval_001",
        status=status,
        approved=status == ApprovalStatus.APPROVED,
        decided_by="security_reviewer",
        decided_at=utc_now_iso(),
        reason=f"Decision changed to {status.value}.",
    )


def test_state_machine_allows_only_pending_to_terminal_decisions() -> None:
    assert (
        ApprovalStateMachine.validate_transition(
            current_status=ApprovalStatus.PENDING,
            next_status=ApprovalStatus.APPROVED,
        ).allowed
        is True
    )

    assert (
        ApprovalStateMachine.validate_transition(
            current_status=ApprovalStatus.PENDING,
            next_status=ApprovalStatus.REJECTED,
        ).allowed
        is True
    )


def test_state_machine_rejects_all_non_pending_transitions() -> None:
    invalid_transitions = [
        (current_status, next_status)
        for current_status, next_status in product(ApprovalStatus, ApprovalStatus)
        if current_status != ApprovalStatus.PENDING
    ]

    assert invalid_transitions

    for current_status, next_status in invalid_transitions:
        result = ApprovalStateMachine.validate_transition(
            current_status=current_status,
            next_status=next_status,
        )

        assert result.allowed is False
        assert "Invalid approval state transition" in result.reason
        assert result.metadata == {
            "guard": "approval-state-transition",
            "current_status": current_status.value,
            "next_status": next_status.value,
        }


def test_state_machine_rejects_pending_to_pending_noop() -> None:
    result = ApprovalStateMachine.validate_transition(
        current_status=ApprovalStatus.PENDING,
        next_status=ApprovalStatus.PENDING,
    )

    assert result.allowed is False
    assert "Invalid approval state transition" in result.reason
    assert result.metadata == {
        "guard": "approval-state-transition",
        "current_status": "pending",
        "next_status": "pending",
    }


def test_authorization_engine_reports_invalid_transition_metadata() -> None:
    engine = ApprovalAuthorizationEngine()

    result = engine.authorize(
        approval_request=build_approval_request(),
        approval_decision=build_approval_decision(ApprovalStatus.REJECTED),
        current_status=ApprovalStatus.APPROVED,
    )

    assert result.allowed is False
    assert "Invalid approval state transition" in result.reason
    assert result.metadata == {
        "guard": "approval-state-transition",
        "current_status": "approved",
        "next_status": "rejected",
    }


def test_authorization_engine_allows_pending_to_rejected_transition() -> None:
    engine = ApprovalAuthorizationEngine()

    result = engine.authorize(
        approval_request=build_approval_request(),
        approval_decision=build_approval_decision(ApprovalStatus.REJECTED),
        current_status=ApprovalStatus.PENDING,
    )

    assert result.allowed is True
    assert result.reason == "Approval rejection authorized."
