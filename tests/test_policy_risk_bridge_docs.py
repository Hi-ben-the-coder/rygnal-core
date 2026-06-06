from pathlib import Path


def test_policy_risk_bridge_doc_exists():
    assert Path("docs/29-policy-risk-bridge.md").exists()


def test_policy_risk_bridge_doc_mentions_supported_fields():
    content = Path("docs/29-policy-risk-bridge.md").read_text()

    required_terms = [
        "PolicyEngine.evaluate(request)",
        "risk_assessment",
        "risk_level",
        "risk_score_min",
        "Existing policy files still work",
    ]

    for term in required_terms:
        assert term in content
