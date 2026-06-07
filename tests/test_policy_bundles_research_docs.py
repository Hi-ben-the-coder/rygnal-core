from pathlib import Path


def test_policy_bundles_research_doc_exists():
    assert Path("docs/36-policy-bundles-research.md").exists()


def test_policy_bundles_research_mentions_future_bundle_layout():
    content = Path("docs/36-policy-bundles-research.md").read_text()

    required_terms = [
        "policies/",
        "bundles/",
        "production-safety.yaml",
        "secrets-protection.yaml",
        "database-safety.yaml",
    ]

    for term in required_terms:
        assert term in content


def test_policy_bundles_research_is_research_only():
    content = Path("docs/36-policy-bundles-research.md").read_text()

    required_terms = [
        "research-only",
        "Do not implement",
        "bundle loader",
        "bundle merge logic",
        "signed bundles",
    ]

    for term in required_terms:
        assert term in content


def test_policy_bundles_research_defines_design_principles():
    content = Path("docs/36-policy-bundles-research.md").read_text()

    required_terms = [
        "Bundles should be versioned",
        "Bundles should be testable",
        "Bundle merge order must be explicit",
        "Conflicting rule IDs should fail validation",
    ]

    for term in required_terms:
        assert term in content
