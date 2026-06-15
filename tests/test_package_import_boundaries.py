from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_rygnal_package_import_does_not_eagerly_import_fastapi() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys, rygnal; print('fastapi' in sys.modules)",
        ],
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "False"


def test_engine_api_module_imports_without_web_api_startup() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "import rygnal.engine_api; print('engine_api import ok')",
        ],
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "engine_api import ok"
