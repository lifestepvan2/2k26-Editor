from __future__ import annotations

import pytest

pytest.importorskip("dearpygui.dearpygui")

from nba2k26_editor.ui import full_player_editor as full_player_editor_mod
from nba2k26_editor.ui.full_player_editor import FullPlayerEditor


def test_sanitize_input_int_range_clamps_to_dpg_int_bounds() -> None:
    lo, hi = FullPlayerEditor._sanitize_input_int_range(-(1 << 60), 1 << 60)
    assert lo == FullPlayerEditor._DPG_INT_MIN
    assert hi == FullPlayerEditor._DPG_INT_MAX


def test_add_field_control_caps_large_integer_bit_length(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, int] = {}

    def _fake_add_input_int(**kwargs):
        captured["min_value"] = int(kwargs.get("min_value", 0))
        captured["max_value"] = int(kwargs.get("max_value", 0))
        captured["default_value"] = int(kwargs.get("default_value", 0))
        return 12345

    monkeypatch.setattr(full_player_editor_mod.dpg, "add_input_int", _fake_add_input_int)

    editor = FullPlayerEditor.__new__(FullPlayerEditor)
    editor.field_meta = {}
    editor._initializing = True

    control = FullPlayerEditor._add_field_control(
        editor,
        category_name="Vitals",
        field_name="Very Large Integer",
        field={"offset": 0, "startBit": 0, "length": 64, "type": "Integer64"},
    )

    assert control == 12345
    assert captured["min_value"] == 0
    assert captured["max_value"] == 999999
    assert captured["default_value"] == 0
