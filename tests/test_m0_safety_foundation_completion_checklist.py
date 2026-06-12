from pathlib import Path

CHECKLIST_PATH = Path("docs/41-m0-safety-foundation-completion-checklist.md")


def test_m0_safety_foundation_completion_checklist_exists() -> None:
    assert CHECKLIST_PATH.exists()


def test_m0_safety_foundation_completion_checklist_covers_closure_gate() -> None:
    content = CHECKLIST_PATH.read_text(encoding="utf-8")

    required_terms = [
        "M0 Safety Foundation — Completion Checklist",
        "Document ID:",
        "Status:",
        "Last updated:",
        "Closure Gate",
        "All M0 implementation issues must be closed.",
        "gh issue list",
        "--repo Rygnal/rygnal-core",
        "--state open",
        '--search "M0"',
        "Local validation and CI validation must both pass.",
    ]

    for term in required_terms:
        assert term in content


def test_m0_safety_foundation_completion_checklist_covers_evidence_matrix() -> None:
    content = CHECKLIST_PATH.read_text(encoding="utf-8")

    required_terms = [
        "Fail-closed default policy",
        "Production-safe policy mode",
        "Policy-risk bridge",
        "Approval request model hardening",
        "Approval state machine",
        "Self-approval guard",
        "Viewer / role approval denial",
        "roles.yaml foundation",
        "Non-interactive approval rejection",
        "Approval timeout rejection",
        "Raw secret leak regression",
        "Audit hash-chain integrity",
        "Branch-complete interceptor enforcement",
        "Runtime modes",
        "Local API safe evaluation",
        "SDK boundary",
    ]

    for term in required_terms:
        assert term in content


def test_m0_safety_foundation_completion_checklist_covers_validation_gate() -> None:
    content = CHECKLIST_PATH.read_text(encoding="utf-8")

    required_commands = [
        "pytest -q --tb=short",
        "ruff check . --fix",
        "ruff format .",
        "ruff format --check .",
        "ruff check .",
        "bandit -r src demo -c pyproject.toml",
        "git diff --check",
    ]

    for command in required_commands:
        assert command in content


def test_m0_safety_foundation_completion_checklist_limits_scope_claims() -> None:
    content = CHECKLIST_PATH.read_text(encoding="utf-8")

    required_terms = [
        "local-first Rygnal Core MVP safety foundation only",
        "Enterprise production readiness",
        "SaaS or multi-tenant readiness",
        "SSO or identity provider integration",
        "SIEM export or external logging pipeline",
        "Hosted audit dashboard or UI",
        "What M0 Does Not Guarantee",
        "These are post-M0 concerns and will be tracked in M1 and beyond.",
    ]

    for term in required_terms:
        assert term in content
