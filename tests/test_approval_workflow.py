from rygnal.approval import (
    ApprovalWorkflow,
    approve_for_testing,
    reject_for_testing,
)
from rygnal.audit_logger import AuditLogger
from rygnal.interceptor import RygnalInterceptor
from rygnal.models import ApprovalStatus, Decision, ExecutionStatus, ToolRequest
from rygnal.policy_engine import load_default_policy_engine
from rygnal.risk_engine import RiskEngine
from rygnal.tool_executor import ToolExecutor


def build_interceptor(tmp_path, approval_workflow=None):
    executor = ToolExecutor()
    logger = AuditLogger(tmp_path / "audit_log.jsonl")

    return RygnalInterceptor(
        policy_engine=load_default_policy_engine(),
        audit_logger=logger,
        tool_executor=executor,
        risk_engine=RiskEngine(),
        approval_workflow=approval_workflow,
    )


def test_default_approval_workflow_rejects_safely():
    workflow = ApprovalWorkflow()

    request = ToolRequest(
        tool_name="file_delete",
        action="delete_file",
        target="customer_data.csv",
    )
    policy_decision = load_default_policy_engine().evaluate(request)

    approval_request, approval_decision = workflow.request_approval(request, policy_decision)

    assert approval_request.approval_id == approval_decision.approval_id
    assert approval_decision.status == ApprovalStatus.REJECTED
    assert approval_decision.approved is False


def test_rejected_approval_required_action_never_executes(tmp_path):
    interceptor = build_interceptor(
        tmp_path,
        approval_workflow=ApprovalWorkflow(resolver=reject_for_testing),
    )

    called = {"value": False}

    def delete_file(request: ToolRequest) -> dict[str, str]:
        called["value"] = True
        return {"deleted": request.target or ""}

    interceptor.tool_executor.register("file_delete", delete_file)

    result = interceptor.intercept(
        ToolRequest(
            tool_name="file_delete",
            action="delete_file",
            target="customer_data.csv",
        )
    )

    assert result.policy_decision.decision == Decision.REQUIRE_APPROVAL
    assert result.approval_decision is not None
    assert result.approval_decision.status == ApprovalStatus.REJECTED
    assert result.execution.status == ExecutionStatus.SKIPPED
    assert result.execution.executed is False
    assert called["value"] is False


def test_approved_action_executes_after_approval(tmp_path):
    interceptor = build_interceptor(
        tmp_path,
        approval_workflow=ApprovalWorkflow(resolver=approve_for_testing),
    )

    called = {"value": False}

    def delete_file(request: ToolRequest) -> dict[str, str]:
        called["value"] = True
        return {"deleted": request.target or ""}

    interceptor.tool_executor.register("file_delete", delete_file)

    result = interceptor.intercept(
        ToolRequest(
            tool_name="file_delete",
            action="delete_file",
            target="customer_data.csv",
        )
    )

    assert result.policy_decision.decision == Decision.REQUIRE_APPROVAL
    assert result.approval_decision is not None
    assert result.approval_decision.status == ApprovalStatus.APPROVED
    assert result.execution.status == ExecutionStatus.EXECUTED
    assert result.execution.executed is True
    assert called["value"] is True


def test_approval_decision_is_stored_in_audit_metadata(tmp_path):
    interceptor = build_interceptor(
        tmp_path,
        approval_workflow=ApprovalWorkflow(resolver=approve_for_testing),
    )

    interceptor.tool_executor.register(
        "file_delete",
        lambda request: {"deleted": request.target or ""},
    )

    result = interceptor.intercept(
        ToolRequest(
            tool_name="file_delete",
            action="delete_file",
            target="customer_data.csv",
        )
    )

    events = interceptor.audit_logger.read_events()

    assert len(events) == 1
    assert events[0].event_id == result.audit_event.event_id
    assert events[0].metadata["approval"]["status"] == "approved"
    assert events[0].metadata["approval"]["approved"] is True
    assert events[0].metadata["risk_score"] >= 60
    assert interceptor.audit_logger.verify_integrity() is True


def test_allowed_action_does_not_create_approval_decision(tmp_path):
    interceptor = build_interceptor(tmp_path)

    interceptor.tool_executor.register(
        "file_read",
        lambda request: {"target": request.target, "content": "safe"},
    )

    result = interceptor.intercept(
        ToolRequest(tool_name="file_read", action="read_file", target="README.md")
    )

    assert result.policy_decision.decision == Decision.ALLOW
    assert result.approval_decision is None
    assert result.execution.status == ExecutionStatus.EXECUTED
