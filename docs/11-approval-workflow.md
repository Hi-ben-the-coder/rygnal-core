# Approval Workflow v1

Approval Workflow v1 adds a human decision layer for actions that require review before execution.

## Goal

When policy returns `require_approval`, Rygnal should not execute the tool automatically.

Instead:

```text
Tool request
→ Risk assessment
→ Policy decision: require_approval
→ Approval request
→ Human approve/reject decision
→ Execute only if approved
→ Audit log stores approval metadata
```
