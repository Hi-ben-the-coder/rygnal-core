from pathlib import Path

from rygnal import Rygnal
from rygnal.approval import ApprovalWorkflow
from rygnal.approval_authorization import ApprovalAuthorizationEngine
from rygnal.models import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
    ExecutionStatus,
    RolePermission,
    Severity,
    ToolRequest,
    utc_now_iso,
)
from rygnal.roles import load_roles_file


def write_roles_yaml(path: Path) -> None:
    path.write_text(
        """
roles:
  viewer:
    role: viewer
    allowed_severities: [low]
    allowed_actions: null
    environments: null

  security_approver:
    role: security_approver
    allowed_severities: [high, critical]
    allowed_actions: [delete_file]
    environments: [local]
"""
    )


def approve_as(*, decided_by: str, reviewer_role: str) -> ApprovalDecision:
    return ApprovalDecision(
        approval_id="",
        status=ApprovalStatus.APPROVED,
        approved=True,
        decided_by=decided_by,
        decided_at=utc_now_iso(),
        reason="Approved after role-based review.",
        metadata={"reviewer_role": reviewer_role},
    )


def test_workflow_loaded_from_roles_yaml_denies_viewer_approval(tmp_path: Path) -> None:
    roles_file = tmp_path / "roles.yaml"
    write_roles_yaml(roles_file)

    def resolver(approval_request):
        return approve_as(
            decided_by="readonly_reviewer",
            reviewer_role="viewer",
        ).model_copy(update={"approval_id": approval_request.approval_id})

    executed = {"value": False}

    def dangerous_delete(_request):
        executed["value"] = True
        return {"deleted": True}

    rygnal = Rygnal(
        audit_log_path=tmp_path / "audit.jsonl",
        approval_workflow=ApprovalWorkflow.from_roles_file(
            resolver=resolver,
            roles_path=roles_file,
        ),
    )
    rygnal.register_tool("file_delete", dangerous_delete)

    result = rygnal.intercept(
        ToolRequest(
            tool_name="file_delete",
            action="delete_file",
            target="customer-data.csv",
            user_id="requester",
            agent_id="demo_agent",
            environment="local",
        )
    )

    assert result.approval_decision is not None
    assert result.approval_decision.status == ApprovalStatus.REJECTED
    assert result.approval_decision.approved is False
    assert result.execution.status == ExecutionStatus.SKIPPED
    assert executed["value"] is False
    assert result.approval_decision.metadata["guard"] == "role-permission"
    assert result.approval_decision.metadata["reviewer_role"] == "viewer"


def test_workflow_loaded_from_roles_yaml_allows_security_approver(tmp_path: Path) -> None:
    roles_file = tmp_path / "roles.yaml"
    write_roles_yaml(roles_file)

    def resolver(approval_request):
        return approve_as(
            decided_by="security_reviewer",
            reviewer_role="security_approver",
        ).model_copy(update={"approval_id": approval_request.approval_id})

    executed = {"value": False}

    def dangerous_delete(_request):
        executed["value"] = True
        return {"deleted": True}

    rygnal = Rygnal(
        audit_log_path=tmp_path / "audit.jsonl",
        approval_workflow=ApprovalWorkflow.from_roles_file(
            resolver=resolver,
            roles_path=roles_file,
        ),
    )
    rygnal.register_tool("file_delete", dangerous_delete)

    result = rygnal.intercept(
        ToolRequest(
            tool_name="file_delete",
            action="delete_file",
            target="customer-data.csv",
            user_id="requester",
            agent_id="demo_agent",
            environment="local",
        )
    )

    assert result.approval_decision is not None
    assert result.approval_decision.status == ApprovalStatus.APPROVED
    assert result.approval_decision.approved is True
    assert result.execution.status == ExecutionStatus.EXECUTED
    assert executed["value"] is True
    assert result.approval_decision.metadata["reviewer_role"] == "security_approver"


def test_role_permissions_enforce_action_environment_and_severity() -> None:
    engine = ApprovalAuthorizationEngine(
        role_permissions={
            "security_approver": RolePermission(
                role="security_approver",
                allowed_severities=[Severity.CRITICAL],
                allowed_actions=["write_file"],
                environments=["production"],
            )
        }
    )

    approval_request = ApprovalRequest(
        requested_by="requester",
        agent_id="demo_agent",
        environment="local",
        tool_name="file_delete",
        action="delete_file",
        target="customer-data.csv",
        reason="Sensitive action requires approval.",
        severity=Severity.HIGH,
    )
    approval_decision = ApprovalDecision(
        approval_id=approval_request.approval_id,
        status=ApprovalStatus.APPROVED,
        approved=True,
        decided_by="security_reviewer",
        decided_at=utc_now_iso(),
        reason="Approved after review.",
        metadata={"reviewer_role": "security_approver"},
    )

    result = engine.authorize(
        approval_request=approval_request,
        approval_decision=approval_decision,
    )

    assert result.allowed is False
    assert result.metadata["guard"] == "role-permission"
    assert result.metadata["denied_constraint"] in {
        "severity",
        "action",
        "environment",
    }


def test_load_roles_file_can_feed_authorization_engine(tmp_path: Path) -> None:
    roles_file = tmp_path / "roles.yaml"
    write_roles_yaml(roles_file)

    engine = ApprovalAuthorizationEngine(role_permissions=load_roles_file(roles_file))

    approval_request = ApprovalRequest(
        requested_by="requester",
        agent_id="demo_agent",
        environment="local",
        tool_name="file_delete",
        action="delete_file",
        target="customer-data.csv",
        reason="Sensitive action requires approval.",
        severity=Severity.HIGH,
    )
    approval_decision = ApprovalDecision(
        approval_id=approval_request.approval_id,
        status=ApprovalStatus.APPROVED,
        approved=True,
        decided_by="security_reviewer",
        decided_at=utc_now_iso(),
        reason="Approved after review.",
        metadata={"reviewer_role": "security_approver"},
    )

    result = engine.authorize(
        approval_request=approval_request,
        approval_decision=approval_decision,
    )

    assert result.allowed is True
    assert result.metadata["reviewer_role"] == "security_approver"
