from __future__ import annotations

from types import SimpleNamespace

import pytest

pytest.importorskip("dearpygui.dearpygui")

from nba2k_editor.ui.app import BoundVar, PlayerEditorApp


class _ScanModelStub:
    def __init__(
        self,
        *,
        teams: list[str] | None = None,
        raise_on_refresh: bool = False,
        hproc: object | None = object(),
    ) -> None:
        self._teams = list(teams or [])
        self._raise_on_refresh = raise_on_refresh
        self.refresh_calls = 0
        self.mem = SimpleNamespace(hproc=hproc)

    def refresh_players(self) -> None:
        self.refresh_calls += 1
        if self._raise_on_refresh:
            raise RuntimeError("refresh failed")

    def get_teams(self) -> list[str]:
        return list(self._teams)


class _ScanAppStub:
    def __init__(self, model: _ScanModelStub) -> None:
        self.model = model
        self.scanning = True
        self.scan_status_var = BoundVar("")
        self.team_scan_status_var = BoundVar("")
        self.team_edit_var = BoundVar("")
        self._pending_team_select: str | None = None
        self.team_dropdown_updates: list[list[str]] = []
        self.player_refresh_calls = 0
        self.team_edit_selected_calls = 0
        self.render_messages: list[str] = []

    def _update_team_dropdown(self, teams: list[str]) -> None:
        self.team_dropdown_updates.append(list(teams))

    def _refresh_player_list(self) -> None:
        self.player_refresh_calls += 1

    def _on_team_edit_selected(self) -> None:
        self.team_edit_selected_calls += 1

    def _render_player_list(self, items=None, message: str | None = None) -> None:
        del items
        self.render_messages.append(message or "")


def test_start_scan_wrapper_uses_shared_flow_without_regression() -> None:
    model = _ScanModelStub(teams=["Celtics", "Lakers"])
    app = _ScanAppStub(model)
    app.scanning = False

    PlayerEditorApp._start_scan(app)

    assert model.refresh_calls == 1
    assert app.render_messages == ["Scanning players..."]
    assert app.scanning is False
    assert app.team_dropdown_updates == [["Celtics", "Lakers"]]
    assert app.player_refresh_calls == 1
    assert app.scan_status_var.get() == ""
    assert app.team_scan_status_var.get() == ""


def test_start_team_scan_wrapper_preserves_pending_selection_behavior() -> None:
    model = _ScanModelStub(teams=["Celtics", "Lakers"])
    app = _ScanAppStub(model)
    app.scanning = False
    app._pending_team_select = "Lakers"

    PlayerEditorApp._start_team_scan(app)

    assert model.refresh_calls == 1
    assert app.render_messages == ["Scanning players..."]
    assert app.team_edit_var.get() == "Lakers"
    assert app.team_edit_selected_calls == 1
    assert app._pending_team_select is None


def test_scan_thread_wrapper_handles_refresh_failure_without_stalling() -> None:
    model = _ScanModelStub(raise_on_refresh=True)
    app = _ScanAppStub(model)

    PlayerEditorApp._scan_thread(app)

    assert app.scanning is False
    assert "failed" in str(app.scan_status_var.get()).lower()


def test_scan_teams_thread_wrapper_handles_refresh_failure_without_stalling() -> None:
    model = _ScanModelStub(raise_on_refresh=True)
    app = _ScanAppStub(model)

    PlayerEditorApp._scan_teams_thread(app)

    assert app.scanning is False
    assert "failed" in str(app.team_scan_status_var.get()).lower()
