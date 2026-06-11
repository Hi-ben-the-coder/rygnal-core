from pathlib import Path

from rygnal.models import Decision, ToolRequest
from rygnal.policy_engine import PolicyEngine


def test_policy_explain_records_rule_evaluation_order_until_match(tmp_path: Path) -> None:
    policy_file = tmp_path / "explain_order_policy.yaml"
    policy_file.write_text(
        """
policy_version: policy.v2
default_decision: allow
rules:
  - id: first-non-match
    priority: 10
    tool_name: shell_command
    decision: block
    severity: critical
    reason: Shell commands are blocked.

  - id: second-match
    priority: 20
    tool_name: file_read
    target_contains: .env
    decision: block
    severity: high
    reason: Env files are blocked.

  - id: third-not-evaluated
    priority: 30
    tool_name: file_read
    decision: allow
    severity: low
    reason: Later allow rule.
"""
    )

    engine = PolicyEngine.from_file(policy_file)
    result = engine.evaluate(ToolRequest(tool_name="file_read", action="read_file", target=".env"))

    assert result.decision == Decision.BLOCK
    assert result.policy_id == "second-match"
    assert result.explanation is not None
    assert result.explanation.matched is True
    assert result.explanation.matched_rule_id == "second-match"
    assert result.explanation.matched_rule_priority == 20
    assert result.explanation.evaluated_rule_ids == [
        "first-non-match",
        "second-match",
    ]
    assert result.explanation.default_decision is False


def test_policy_explain_records_all_rule_ids_for_default_decision(tmp_path: Path) -> None:
    policy_file = tmp_path / "explain_default_policy.yaml"
    policy_file.write_text(
        """
policy_version: policy.v2
default_decision: require_approval
rules:
  - id: block-env
    priority: 10
    tool_name: file_read
    target_contains: .env
    decision: block
    severity: high
    reason: Env files are blocked.

  - id: block-dangerous-shell
    priority: 20
    tool_name: shell_command
    input_contains: rm -rf
    decision: block
    severity: critical
    reason: Dangerous shell commands are blocked.
"""
    )

    engine = PolicyEngine.from_file(policy_file)
    result = engine.evaluate(
        ToolRequest(tool_name="file_read", action="read_file", target="README.md")
    )

    assert result.decision == Decision.REQUIRE_APPROVAL
    assert result.allowed is False
    assert result.policy_id is None
    assert result.explanation is not None
    assert result.explanation.matched is False
    assert result.explanation.matched_rule_id is None
    assert result.explanation.matched_rule_priority is None
    assert result.explanation.matched_conditions == []
    assert result.explanation.evaluated_rule_ids == [
        "block-env",
        "block-dangerous-shell",
    ]
    assert result.explanation.default_decision is True


def test_policy_explain_records_risk_match_conditions(tmp_path: Path) -> None:
    policy_file = tmp_path / "explain_risk_policy.yaml"
    policy_file.write_text(
        """
policy_version: policy.v2
default_decision: allow
rules:
  - id: block-critical-risk
    priority: 10
    risk_level: critical
    risk_score_min: 90
    decision: block
    severity: critical
    reason: Critical risk is blocked.
"""
    )

    engine = PolicyEngine.from_file(policy_file)
    result = engine.evaluate(
        ToolRequest(tool_name="file_read", action="read_file", target=".env"),
        risk_assessment={
            "risk_level": "critical",
            "risk_score": 95,
        },
    )

    assert result.decision == Decision.BLOCK
    assert result.policy_id == "block-critical-risk"
    assert result.explanation is not None
    assert result.explanation.matched is True
    assert result.explanation.matched_conditions == [
        "risk_level",
        "risk_score_min",
    ]
    assert result.explanation.evaluated_rule_ids == ["block-critical-risk"]
    assert result.explanation.default_decision is False
