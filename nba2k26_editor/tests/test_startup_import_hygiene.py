from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("dearpygui.dearpygui")


def test_ui_app_import_does_not_eager_load_heavy_agent_dependencies() -> None:
    project_root = Path(__file__).resolve().parents[2]
    script = (
        "import json, sys; "
        "import nba2k26_editor.ui.app; "
        "print(json.dumps({'torch': 'torch' in sys.modules, 'pandas': 'pandas' in sys.modules}))"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    assert lines, "Expected subprocess output with dependency flags."
    payload = json.loads(lines[-1])
    assert payload == {"torch": False, "pandas": False}
