from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from nba2k_editor.core.perf import clear, summarize
from nba2k_editor.importing.excel_import import export_excel_workbook, import_excel_workbook

openpyxl = pytest.importorskip("openpyxl")


class _StubModel:
    def __init__(self) -> None:
        self.players = []
        self.team_list = [(1, "Lakers"), (2, "Celtics")]
        self.staff_list = []
        self.stadium_list = []
        self.writes = 0
        self.reads = 0

    def get_categories_for_super(self, super_type: str):
        if super_type == "Teams":
            return {
                "Team Vitals": [
                    {
                        "category": "Team Vitals",
                        "name": "Team Name",
                        "address": 0,
                        "length": 32,
                        "startBit": 0,
                        "type": "wstring",
                    }
                ]
            }
        return {}

    def encode_field_value(self, **kwargs):
        self.writes += 1
        return True

    def decode_field_value(self, **kwargs):
        self.reads += 1
        idx = int(kwargs.get("entity_index", 0))
        return "Lakers" if idx == 1 else "Celtics"


def _build_workbook(path: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Team Vitals"
    ws.cell(row=1, column=1, value="Team Name")
    ws.cell(row=2, column=1, value="Lakers")
    ws.cell(row=3, column=1, value="Celtics")
    wb.save(path)


def test_import_export_perf_harness(tmp_path: Path):
    os.environ["NBA2K_EDITOR_PROFILE"] = "1"
    clear()
    template = tmp_path / "teams_template.xlsx"
    import_path = tmp_path / "teams_import.xlsx"
    output_path = tmp_path / "teams_export.xlsx"
    _build_workbook(template)
    _build_workbook(import_path)
    model = _StubModel()
    start = time.perf_counter()
    import_result = import_excel_workbook(model, import_path, "teams")
    export_result = export_excel_workbook(model, output_path, "teams", template_path=template)
    elapsed = time.perf_counter() - start
    threshold = float(os.getenv("NBA2K_EDITOR_PERF_IMPORT_MAX", "8.0"))
    assert elapsed <= threshold
    assert import_result.rows_seen >= 2
    assert export_result.rows_written >= 2
    stats = summarize()
    assert "excel_import.import_workbook" in stats
    assert "excel_import.export_workbook" in stats

