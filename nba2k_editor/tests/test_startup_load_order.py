from __future__ import annotations

from types import SimpleNamespace

import pytest

from nba2k_editor.core import offsets as offsets_mod
from nba2k_editor.models import data_model as data_model_mod
from nba2k_editor.models.data_model import PlayerDataModel

pytest.importorskip("dearpygui.dearpygui")
from nba2k_editor.ui import app as app_module
from nba2k_editor.ui.app import PlayerEditorApp


class _StubMem:
    def __init__(self) -> None:
        self.module_name = "nba2k26.exe"
        self.hproc = None
        self.base_addr = None

    def open_process(self) -> bool:
        return False


class _AppModelStub:
    def __init__(self) -> None:
        self.mem = SimpleNamespace(module_name="nba2k26.exe", hproc=None)

    def get_teams(self) -> list[str]:
        return []


def test_model_init_does_not_reinitialize_offsets_for_loaded_target(monkeypatch: pytest.MonkeyPatch) -> None:
    call_count = 0

    def _fake_initialize_offsets(
        target_executable: str | None = None,
        force: bool = False,
        base_pointer_overrides: dict[str, int] | None = None,
        filename: str | None = None,
    ) -> None:
        nonlocal call_count
        del target_executable, force, base_pointer_overrides, filename
        call_count += 1

    monkeypatch.setattr(data_model_mod, "initialize_offsets", _fake_initialize_offsets)
    monkeypatch.setattr(data_model_mod, "_load_categories", lambda: {})
    monkeypatch.setattr(data_model_mod.PlayerDataModel, "_sync_offset_constants", lambda self: None)
    monkeypatch.setattr(data_model_mod.PlayerDataModel, "_resolve_name_fields", lambda self: None)

    offsets_mod._offset_config = {"offsets": []}
    offsets_mod._current_offset_target = "nba2k26.exe"
    PlayerDataModel(_StubMem())

    assert call_count == 0