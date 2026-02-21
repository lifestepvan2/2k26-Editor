from __future__ import annotations

import os
import time

import pytest

from nba2k_editor.core import offsets as offsets_mod
from nba2k_editor.core.perf import clear, summarize
from nba2k_editor.models import data_model as data_model_mod

pytest.importorskip("dearpygui.dearpygui")
from nba2k_editor.entrypoints import gui


class _StubMem:
    def __init__(self, module_name: str) -> None:
        self.module_name = module_name
        self.hproc = None
        self.base_addr = None

    def open_process(self) -> bool:
        return False


class _StubModel:
    def __init__(self, mem, max_players: int = 0) -> None:
        self.mem = mem
        self.max_players = max_players


class _StubApp:
    def __init__(self, model) -> None:
        self.model = model


def test_gui_startup_perf_harness(monkeypatch):
    monkeypatch.setattr(gui.sys, "platform", "win32")
    monkeypatch.setattr(gui, "GameMemory", _StubMem)
    monkeypatch.setattr(gui, "PlayerDataModel", _StubModel)
    monkeypatch.setattr(gui, "PlayerEditorApp", _StubApp)
    monkeypatch.setattr(gui, "initialize_offsets", lambda *args, **kwargs: None)
    monkeypatch.setattr(gui, "_launch_with_dearpygui", lambda *args, **kwargs: None)

    os.environ["NBA2K_EDITOR_PROFILE"] = "1"
    clear()
    start = time.perf_counter()
    gui.main()
    elapsed = time.perf_counter() - start
    threshold = float(os.getenv("NBA2K_EDITOR_PERF_STARTUP_MAX", "5.0"))
    assert elapsed <= threshold
    stats = summarize()
    assert "gui.main" in stats


def test_gui_startup_does_not_reinitialize_offsets_in_model(monkeypatch):
    monkeypatch.setattr(gui.sys, "platform", "win32")
    monkeypatch.setattr(gui, "GameMemory", _StubMem)
    monkeypatch.setattr(gui, "PlayerDataModel", data_model_mod.PlayerDataModel)
    monkeypatch.setattr(gui, "PlayerEditorApp", _StubApp)
    monkeypatch.setattr(gui, "_launch_with_dearpygui", lambda *args, **kwargs: None)

    calls: list[tuple[str, bool, str | None]] = []

    def _fake_initialize_offsets(
        target_executable: str | None = None,
        force: bool = False,
        base_pointer_overrides: dict[str, int] | None = None,
        filename: str | None = None,
    ) -> None:
        del base_pointer_overrides
        target_exec = target_executable or offsets_mod.MODULE_NAME
        calls.append((str(target_exec), bool(force), filename))
        offsets_mod._offset_config = {"offsets": []}
        offsets_mod._current_offset_target = str(target_exec).lower()
        offsets_mod.MODULE_NAME = str(target_exec)

    monkeypatch.setattr(gui, "initialize_offsets", _fake_initialize_offsets)
    monkeypatch.setattr(data_model_mod, "initialize_offsets", _fake_initialize_offsets)
    monkeypatch.setattr(data_model_mod, "_load_categories", lambda: {})
    monkeypatch.setattr(data_model_mod.PlayerDataModel, "_sync_offset_constants", lambda self: None)
    monkeypatch.setattr(data_model_mod.PlayerDataModel, "_resolve_name_fields", lambda self: None)

    offsets_mod._offset_config = None
    offsets_mod._current_offset_target = None
    gui.main()

    # Startup should initialize offsets once in entrypoint; model init should reuse loaded target.
    assert len(calls) == 1
    assert calls[0][1] is True