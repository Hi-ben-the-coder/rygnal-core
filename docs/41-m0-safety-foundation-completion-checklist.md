# M0 Safety Foundation — Completion Checklist

**Document ID:** `docs/41-m0-safety-foundation-completion-checklist.md`
**Status:** In review — pending closure gate validation
**Last updated:** 2026-06-12

---

## Overview

This document defines the completion criteria for the Rygnal Core M0 Safety Foundation milestone. M0 is considered complete when this checklist PR is merged and the validation gate is fully green.

### Scope

This checklist covers the **local-first Rygnal Core MVP safety foundation only.**

The following are explicitly **out of scope** for M0:

- Enterprise production readiness
- SaaS or multi-tenant readiness
- SSO or identity provider integration
- SIEM export or external logging pipeline
- Hosted audit dashboard or UI

---

## Closure Gate

The following conditions must all be true before this PR is merged.

**1. All M0 implementation issues must be closed.**

Run this command to verify:

```bash
gh issue list \
  --repo Rygnal/rygnal-core \
  --state open \
  --search "M0"
```

While this PR is open, only the checklist issue itself should appear.
After this PR merges, the same command must return zero open issues.

**2. Local validation and CI validation must both pass.**

See the [Required Validation Gate](#required-validation-gate) section below.

---

## M0 Safety Foundation — Evidence Matrix

Each row defines a required safety behaviour and the test files that prove it.

| Area | Required Safety Behaviour | Evidence |
|---|---|---|
| **Fail-closed default policy** | Unknown or unmatched tool actions must not be allowed by default. | `policies/default_policy.yaml` · `tests/test_default_policy_production_safety.py` · `tests/test_policy_default_decision.py` |
| **Production-safe policy mode** | Production-safe mode must require approval by default and block critical-risk actions. | `policies/production_safe_policy.yaml` · `tests/test_production_safe_policy_mode.py` |
| **Policy-risk bridge** | Policy evaluation must receive and correctly use risk context from the risk engine. | `tests/test_policy_risk_bridge.py` |
| **Approval request model hardening** | Approval context must preserve required identity and context fields, and reject invalid approval input. | `tests/test_approval_request_model_hardening.py` |
| **Approval state machine** | Approval states must follow valid transitions and reject invalid state changes. | `tests/test_approval_state_machine.py` |
| **Self-approval guard** | A requester must never be able to approve their own request. | `tests/test_self_approval_guard.py` · `tests/test_approval_authorization_engine.py` |
| **Viewer / role approval denial** | Read-only or viewer-role reviewers must not be able to authorise approval execution. | `tests/test_viewer_role_approval_denial.py` · `tests/test_roles_yaml_approval_authorization_integration.py` |
| **roles.yaml foundation** | Operator role permissions must load from configuration and reject invalid role definitions. | `policies/roles.yaml` · `tests/test_roles_yaml_loader.py` · `tests/test_role_permission_model.py` |
| **Non-interactive approval rejection** | Non-interactive CLI approval must reject by default and never prompt for input. | `tests/test_cli_approval_workflow.py` |
| **Approval timeout rejection** | CLI approval timeout or interruption must reject by default, skip execution, and preserve audit metadata. | `tests/test_cli_approval_workflow.py` |
| **Raw secret leak regression** | Raw secrets must never be persisted in audit JSONL output. | `tests/test_raw_secret_leak_regression.py` · `tests/test_security_hardening.py` |
| **Audit hash-chain integrity** | Audit events must form a tamper-evident hash chain, including previous-hash link validation. | `tests/test_audit_logger.py` · `tests/test_sqlite_audit_storage.py` |
| **Branch-complete interceptor enforcement** | Interceptor execution branches must cover: allow, block, approval approved, approval rejected, simulate, and observe. | `tests/test_interceptor_branch_complete.py` |
| **Runtime modes** | Observe and simulate modes must never execute real tools. | `tests/test_runtime_modes.py` |
| **Local API safe evaluation** | Local API evaluation must support safe audit generation without side effects. | `tests/test_local_fastapi_service.py` |
| **SDK boundary** | Public wrapper usage must preserve policy, risk, audit, and execution behaviour end-to-end. | `tests/test_sdk_boundary.py` |

---

## Required Validation Gate

Run the full validation sequence below before opening or merging this PR.
**Every command must exit with code 0.** Any failure blocks merge.

```bash
# 1. Full test suite — no failures, no skipped safety tests
pytest -q --tb=short

# 2. Lint — auto-fix safe issues
ruff check . --fix

# 3. Format — apply formatting
ruff format .

# 4. Format check — confirm no unformatted files remain
ruff format --check .

# 5. Lint check — confirm no remaining lint errors
ruff check .

# 6. Security scan — no high or critical findings in src or demo
bandit -r src demo -c pyproject.toml

# 7. Whitespace check — no trailing whitespace or conflict markers
git diff --check
```

### Expected Output

| Command | Expected Result |
|---|---|
| `pytest` | All tests pass, 0 failures |
| `ruff check` | 0 errors |
| `ruff format --check` | 0 unformatted files |
| `bandit` | 0 high or critical issues |
| `git diff --check` | Clean — no whitespace errors |

---

## Definition of Done

M0 Safety Foundation is complete when all of the following are true:

- All rows in the evidence matrix have passing tests in CI
- The closure gate commands return clean output
- This PR is merged to `main`
- No open GitHub issues are labelled or tagged `M0`

---

## What M0 Does Not Guarantee

M0 establishes a local safety foundation. It does not guarantee:

- Correctness under adversarial network conditions
- Safety under concurrent multi-agent workloads
- Compliance with any regulatory framework (SOC 2, ISO 27001, GDPR)
- Production SLA or uptime commitments

These are post-M0 concerns and will be tracked in M1 and beyond.
