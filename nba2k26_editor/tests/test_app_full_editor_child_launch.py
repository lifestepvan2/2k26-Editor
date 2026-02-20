from __future__ import annotations

from types import SimpleNamespace

import pytest

pytest.importorskip("dearpygui.dearpygui")

from nba2k26_editor.ui import app as app_module
from nba2k26_editor.ui.app import BoundVar, PlayerEditorApp


class _MemStub:
    def __init__(self, open_ok: bool = True) -> None:
        self._open_ok = open_ok
        self.module_name = "nba2k26.exe"
        self.hproc = object() if open_ok else None

    def open_process(self) -> bool:
        self.hproc = object() if self._open_ok else None
        return self._open_ok


class _ModelStub:
    def __init__(self, *, open_ok: bool = True, teams: list[str] | None = None, team_idx: int | None = None) -> None:
        self.mem = _MemStub(open_ok=open_ok)
        self._teams = list(teams or [])
        self._team_idx = team_idx
        self.refresh_players_calls = 0

    def refresh_players(self) -> None:
        self.refresh_players_calls += 1

    def get_teams(self) -> list[str]:
        return list(self._teams)

    def _team_index_for_display_name(self, display_name: str) -> int | None:
        if self._team_idx is None:
            return None
        if display_name in self._teams:
            return self._team_idx
        return None

    def get_staff(self) -> list[str]:
        return []

    def get_stadiums(self) -> list[str]:
        return []


def test_open_full_editor_launches_child_with_player_indices(monkeypatch) -> None:
    model = _ModelStub(open_ok=True)
    app = PlayerEditorApp(model)
    app.selected_players = [SimpleNamespace(index=7), SimpleNamespace(index=21), SimpleNamespace(index=7)]
    launches: list[dict[str, object]] = []
    errors: list[tuple[str, str]] = []

    monkeypatch.setattr(app_module, "launch_full_editor_process", lambda **kwargs: launches.append(kwargs))
    app.show_error = lambda title, message: errors.append((title, message))  # type: ignore[assignment]

    app._open_full_editor()

    assert launches == [{"editor": "player", "indices": [7, 21]}]
    assert errors == []


def test_open_full_team_editor_launches_child_with_resolved_team_index(monkeypatch) -> None:
    model = _ModelStub(open_ok=True, teams=["Bulls"], team_idx=3)
    app = PlayerEditorApp(model)
    app.team_edit_var = BoundVar("Bulls")
    launches: list[dict[str, object]] = []
    errors: list[tuple[str, str]] = []
    infos: list[tuple[str, str]] = []

    monkeypatch.setattr(app_module, "launch_full_editor_process", lambda **kwargs: launches.append(kwargs))
    app.show_error = lambda title, message: errors.append((title, message))  # type: ignore[assignment]
    app.show_info = lambda title, message: infos.append((title, message))  # type: ignore[assignment]

    app._open_full_team_editor()

    assert launches == [{"editor": "team", "index": 3}]
    assert errors == []
    assert infos == []


def test_open_full_staff_editor_launches_selected_scanned_index(monkeypatch) -> None:
    model = _ModelStub(open_ok=True)
    app = PlayerEditorApp(model)
    app.staff_listbox_tag = "staff_tag"
    app._filtered_staff_entries = [(10, "Alpha"), (45, "Bravo")]
    launches: list[dict[str, object]] = []
    monkeypatch.setattr(app_module, "launch_full_editor_process", lambda **kwargs: launches.append(kwargs))
    monkeypatch.setattr(app_module.dpg, "does_item_exist", lambda _tag: True)
    monkeypatch.setattr(app_module.dpg, "get_value", lambda _tag: "Bravo")

    app._open_full_staff_editor()

    assert launches == [{"editor": "staff", "index": 45}]


def test_selected_staff_indices_return_scanned_id_not_filtered_position(monkeypatch) -> None:
    model = _ModelStub(open_ok=True)
    app = PlayerEditorApp(model)
    app.staff_listbox_tag = "staff_tag"
    app._filtered_staff_entries = [(4, "First"), (22, "Second")]
    monkeypatch.setattr(app_module.dpg, "does_item_exist", lambda _tag: True)
    monkeypatch.setattr(app_module.dpg, "get_value", lambda _tag: "Second")

    assert app.get_selected_staff_indices() == [22]


def test_selected_stadium_indices_return_scanned_id_not_filtered_position(monkeypatch) -> None:
    model = _ModelStub(open_ok=True)
    app = PlayerEditorApp(model)
    app.stadium_listbox_tag = "stadium_tag"
    app._filtered_stadium_entries = [(1, "Arena A"), (99, "Arena B")]
    monkeypatch.setattr(app_module.dpg, "does_item_exist", lambda _tag: True)
    monkeypatch.setattr(app_module.dpg, "get_value", lambda _tag: "Arena B")

    assert app.get_selected_stadium_indices() == [99]
