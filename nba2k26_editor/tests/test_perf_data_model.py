from __future__ import annotations

import os
import time

from nba2k_editor.core import offsets as offsets_mod
from nba2k_editor.core.perf import clear, summarize
from nba2k_editor.models import data_model as data_model_mod
from nba2k_editor.models.data_model import PlayerDataModel


class _StubMem:
    def __init__(self) -> None:
        self.module_name = "nba2k26.exe"
        self.hproc = None
        self.base_addr = None

    def open_process(self) -> bool:
        return False


def test_data_model_refresh_perf_harness():
    os.environ["NBA2K_EDITOR_PROFILE"] = "1"
    clear()
    model = PlayerDataModel(_StubMem())
    start = time.perf_counter()
    model.refresh_players()
    model.refresh_staff()
    model.refresh_stadiums()
    elapsed = time.perf_counter() - start
    threshold = float(os.getenv("NBA2K_EDITOR_PERF_DATA_MODEL_MAX", "5.0"))
    assert elapsed <= threshold
    stats = summarize()
    assert "data_model.refresh_players" in stats
    assert "data_model.refresh_staff" in stats
    assert "data_model.refresh_stadiums" in stats


def test_data_model_init_reuses_loaded_offsets_for_same_target(monkeypatch):
    calls: list[tuple[str, bool]] = []

    def _fake_initialize_offsets(
        target_executable: str | None = None,
        force: bool = False,
        base_pointer_overrides: dict[str, int] | None = None,
        filename: str | None = None,
    ) -> None:
        del base_pointer_overrides, filename
        target_exec = target_executable or offsets_mod.MODULE_NAME
        calls.append((str(target_exec), bool(force)))
        offsets_mod._offset_config = {"offsets": []}
        offsets_mod._current_offset_target = str(target_exec).lower()

    monkeypatch.setattr(data_model_mod, "initialize_offsets", _fake_initialize_offsets)
    monkeypatch.setattr(data_model_mod, "_load_categories", lambda: {})
    monkeypatch.setattr(data_model_mod.PlayerDataModel, "_sync_offset_constants", lambda self: None)
    monkeypatch.setattr(data_model_mod.PlayerDataModel, "_resolve_name_fields", lambda self: None)

    offsets_mod._offset_config = {"offsets": []}
    offsets_mod._current_offset_target = "nba2k26.exe"
    PlayerDataModel(_StubMem())

    # When offsets are already loaded for the active target, model init should not call initialize_offsets again.
    assert calls == []
