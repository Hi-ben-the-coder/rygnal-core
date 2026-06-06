# Policy Risk Bridge

Policy Risk Bridge allows Policy Engine rules to optionally use Risk Engine output.

## Goal

Let policies match risk context without breaking existing policy behavior.

## What Changed

- `PolicyEngine.evaluate(request)` still works
- `PolicyEngine.evaluate(request, risk_assessment=assessment)` is now supported
- Policy rules can match `risk_level`
- Policy rules can match `risk_score_min`

## Why

Risk Engine v2 produces structured risk assessments. Policy Engine needs a clean way to consume that context.

## Supported Risk Fields

- `risk_level`
- `risk_score_min`

## Compatibility

Existing policy files still work.

Risk-aware rules only match when risk assessment data is provided.

## Not Included Yet

- Chain-risk matching
- Signal ID matching
- Runtime mode matching
- Policy bundle support
