from pathlib import Path


def read(path: str) -> str:
    return Path(path).read_text()


def test_v01_documentation_files_exist():
    required_files = [
        "README.md",
        "docs/architecture.md",
        "docs/known-limitations.md",
        "docs/v0.1-scope.md",
        "docs/getting-started.md",
        "docs/security-model.md",
    ]

    for file_path in required_files:
        assert Path(file_path).exists(), f"Missing documentation file: {file_path}"


def test_readme_is_honest_about_current_status():
    content = read("README.md")
    assert "local-first core MVP" in content
    assert "not a full saas product" in content.lower()
    assert "not enterprise production-ready" in content.lower()


def test_known_limitations_are_documented():
    content = read("docs/known-limitations.md")
    assert "No Real AI-Agent Integration Yet" in content
    assert "No SaaS Layer" in content
    assert "not yet a complete product" in content.lower()


def test_architecture_doc_contains_core_flow():
    content = read("docs/architecture.md")
    assert "RygnalInterceptor" in content
    assert "RiskEngine" in content
    assert "PolicyEngine" in content
    assert "AuditLogger" in content
    assert "ToolExecutor" in content


def test_getting_started_contains_demo_commands():
    content = read("docs/getting-started.md")
    assert "python -m demo.run_demo" in content
    assert "docker compose build" in content
    assert "make validate" in content


def test_security_model_documents_core_controls():
    content = read("docs/security-model.md")
    assert "Policy Enforcement" in content
    assert "Risk Scoring" in content
    assert "Audit Logging" in content
    assert "Tool Safety" in content
