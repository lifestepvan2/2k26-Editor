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


def test_show_ai_builds_screen_and_starts_bridge_lazily(monkeypatch: pytest.MonkeyPatch) -> None:
    build_calls = 0

    def _fake_build_ai(app) -> None:
        nonlocal build_calls
        build_calls += 1
        app.screen_tags["ai"] = "screen_ai"

    monkeypatch.setattr(app_module, "build_ai_screen", _fake_build_ai)
    app = PlayerEditorApp(_AppModelStub())
    app._lazy_screen_builders["ai"] = _fake_build_ai

    shown: list[str] = []
    app._show_screen = lambda key: shown.append(key)  # type: ignore[assignment]

    bridge_calls = 0

    def _fake_start_bridge() -> None:
        nonlocal bridge_calls
        bridge_calls += 1
        app.control_bridge = object()

    app._start_control_bridge = _fake_start_bridge  # type: ignore[assignment]

    assert app.control_bridge is None
    app.show_ai()
    app.show_ai()

    assert build_calls == 1
    assert bridge_calls == 1
    assert shown == ["ai", "ai"]


def test_show_agent_starts_polling_only_after_screen_is_opened(monkeypatch: pytest.MonkeyPatch) -> None:
    build_calls = 0

    def _fake_build_agent(app) -> None:
        nonlocal build_calls
        build_calls += 1
        app.screen_tags["agent"] = "screen_agent"

    monkeypatch.setattr(app_module, "build_agent_screen", _fake_build_agent)
    app = PlayerEditorApp(_AppModelStub())
    app._lazy_screen_builders["agent"] = _fake_build_agent

    shown: list[str] = []
    app._show_screen = lambda key: shown.append(key)  # type: ignore[assignment]

    poll_calls = 0

    def _fake_start_polling() -> None:
        nonlocal poll_calls
        if app.agent_polling:
            return
        poll_calls += 1
        app.agent_polling = True

    app._start_agent_polling = _fake_start_polling  # type: ignore[assignment]

    assert app.agent_polling is False
    app.show_agent()
    app.show_agent()

    assert build_calls == 1
    assert poll_calls == 1
    assert shown == ["agent", "agent"]
