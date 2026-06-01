# Rygnal Core

Rygnal Core is a local-first core MVP for runtime governance of AI-agent tool actions. It is not a full SaaS product, enterprise deployment, or enterprise production-ready platform. It is not enterprise production-ready.

## What Works Today

- Policy Engine v1
- Risk Engine v1
- Audit Logger v1
- Runtime Interceptor v1
- Approval Workflow v1
- Runtime Modes v1
- Real Scenario Runner v1
- CLI Output v1
- Security Hardening v1
- Docker setup
- CI validation

## What is Not Included Yet

- SaaS dashboard
- Login/auth system
- Billing
- Multi-tenant workspaces
- Real AI-agent integration
- MCP gateway
- Enterprise SSO
- SIEM export
- Cloud deployment

## Run Locally

```bash
make install
make validate
```

Run the demo:

```bash
python -m demo.run_demo
```

## Run with Docker

```bash
docker compose build
docker compose run --rm rygnal python -m demo.run_demo
```

## Validation

```bash
ruff format src tests demo
ruff check src tests demo
pytest -q
bandit -r src demo -c pyproject.toml
pip-audit -r requirements-dev.txt
python -m demo.run_demo
```

## License

Private repository. No public license selected yet.
