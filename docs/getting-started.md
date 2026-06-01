# Getting Started

## Requirements

- Python 3.11+
- Git
- Docker optional but recommended

## Setup

```bash
git clone https://github.com/Rygnal/rygnal-core.git
cd rygnal-core
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Run Validation

```bash
make validate
```

Or manually:

```bash
ruff format src tests demo
ruff check src tests demo
pytest -q
bandit -r src demo -c pyproject.toml
pip-audit -r requirements-dev.txt
python -m demo.run_demo
```

## Run Demo

```bash
python -m demo.run_demo
```

## Run with Docker

```bash
docker compose build
docker compose run --rm rygnal python -m demo.run_demo
```

## Expected Demo Behavior

The demo should show:

- safe file read allowed
- `.env` access blocked
- file delete requires approval
- dangerous shell command blocked
- external secret send simulated
- safe file write allowed
- runtime mode shown as enforce
- audit event IDs generated
