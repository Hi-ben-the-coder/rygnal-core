# Policy Bundles Research

## Goal

Research how Rygnal should structure reusable policy bundles in the future.

This is research-only. It does not implement bundle loading yet.

## Current State

Rygnal currently has:

- `policies/default_policy.yaml`
- example policies in `examples/policies/`
- test fixtures in `tests/fixtures/policies/`
- richer policy match fields
- risk-aware policy matching

## Problem

A single default policy file is useful for MVP, but long term Rygnal needs reusable policy bundles for different environments and use cases.

Examples:

- local development bundle
- production safety bundle
- secrets protection bundle
- external data sharing bundle
- database mutation bundle
- MCP tool safety bundle
- high-risk agent bundle

## Proposed Bundle Layout

Future layout:

    policies/
      default_policy.yaml
      roles.yaml
      bundles/
        local-dev.yaml
        production-safety.yaml
        secrets-protection.yaml
        external-data.yaml
        database-safety.yaml
        mcp-tools.yaml

## Bundle Concept

A policy bundle should be a named group of policy rules.

Each bundle should include:

- bundle name
- bundle version
- description
- rules
- intended environment
- risk focus
- compatibility notes

## Example Bundle Shape

    bundle_name: production-safety
    bundle_version: 0.1.0
    description: Production safety policies for risky AI-agent actions.
    applies_to:
      environments: [production]
    rules:
      - id: block-production-secret-read
        priority: 10
        tool_name: file_read
        target_contains: ".env"
        decision: block
        severity: critical
        reason: Production secret reads are blocked.

## Design Principles

- Bundles should be deterministic
- Bundles should be versioned
- Bundles should be testable
- Bundles should not silently override each other
- Bundle merge order must be explicit
- Conflicting rule IDs should fail validation
- Default bundle should stay conservative

## What Not To Build Yet

Do not implement these in this issue:

- bundle loader
- bundle merge logic
- bundle CLI commands
- remote policy registry
- enterprise policy marketplace
- signed bundles

## Recommended Future Phases

### Phase 1: Research

Document bundle structure and rules.

### Phase 2: Bundle Fixtures

Add example bundle YAML files.

### Phase 3: Bundle Loader

Load one or more bundles into PolicyEngine.

### Phase 4: Conflict Validation

Detect duplicate rule IDs and unsafe overrides.

### Phase 5: CLI Support

Add commands like:

    rygnal policy bundle list
    rygnal policy bundle validate

## Decision

Rygnal should support policy bundles later, but not before the current policy engine and approval authorization layers are stable.
