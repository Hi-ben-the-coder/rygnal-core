# Known Limitations

Rygnal Core v0.1 is intentionally scoped as a local-first MVP.

## Not Production-Ready Yet

Rygnal Core v0.1 should not be presented as an enterprise production runtime security layer yet.

It is a strong local prototype and architecture foundation.

## No Real AI-Agent Integration Yet

The scenario runner creates controlled tool requests.

Rygnal is not yet connected to:

- OpenAI tool calling
- LangChain
- MCP
- AutoGen
- CrewAI
- production agent systems

## Approval Workflow is Basic

Approval workflow exists, but it is not yet a full human approval system.

Missing:

- approval UI
- notification
- timeout handling in real workflows
- approval queue
- approver roles
- approval API

## Policy Engine is Basic

Current policy engine uses simple YAML rules.

Limitations:

- no complex contextual logic
- no policy versioning
- no policy priority system
- no OPA/Rego support yet
- no organization-level policy management

## Risk Engine is Rules-Based

Risk scoring is deterministic and useful for MVP, but it is not complete.

Known gaps:

- hardcoded signals
- limited secret target patterns
- no dynamic threat intelligence
- no agent behavior history
- no environment-specific tuning

## Tool Adapters are Local/Sandboxed

Current adapters are controlled local adapters.

They are not full production adapters.

## External API Adapter is Dry-Run

External send does not perform real network transmission in v0.1.

This is intentional for safety.

## No SaaS Layer

Missing:

- dashboard
- auth
- billing
- teams
- organizations
- deployment model
- audit viewer
- policy editor

## Summary

Rygnal Core v0.1 is useful for architecture validation, local demos, and core runtime development.

It is not yet a complete product.
