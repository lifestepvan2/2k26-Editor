from __future__ import annotations

from types import SimpleNamespace

import pytest

pytest.importorskip("dearpygui.dearpygui")

from nba2k26_editor.ui import app as app_module
from nba2k26_editor.ui.app import BoundVar, PlayerEditorApp
import dearpygui.dearpygui as dpg


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

    def run_on_ui_thread(self, func, delay_ms: int = 0) -> None:
        assert delay_ms == 0
        func()

    def _update_team_dropdown(self, teams: list[str]) -> None:
        self.team_dropdown_updates.append(list(teams))

    def _refresh_player_list(self) -> None:
        self.player_refresh_calls += 1

    def _on_team_edit_selected(self) -> None:
        self.team_edit_selected_calls += 1

    def _render_player_list(self, items=None, message: str | None = None) -> None:
        del items
        self.render_messages.append(message or "")


class _TradeModelStub:
    def __init__(self, team_list: list[tuple[int, str]], refresh_result: list[tuple[int, str]]) -> None:
        self.team_list = list(team_list)
        self._refresh_result = list(refresh_result)
        self.refresh_calls = 0

    def refresh_players(self) -> None:
        self.refresh_calls += 1
        self.team_list = list(self._refresh_result)


class _TradeAppStub:
    def __init__(self, model: _TradeModelStub) -> None:
        self.model = model
        self.trade_team_options: list[str] = []
        self.trade_team_lookup: dict[str, int] = {}
        self.trade_participants: list[str] = []
        self.trade_active_team_var = BoundVar("")
        self.trade_add_team_combo_tag = None
        self.trade_participants_list_tag = None
        self.trade_active_team_combo_tag = None
        self.ensure_slot_calls = 0
        self.render_calls = 0

    def _trade_ensure_slot_entries(self) -> None:
        self.ensure_slot_calls += 1

    def _trade_render_team_lists(self) -> None:
        self.render_calls += 1


class _AppModelStub:
    def __init__(self) -> None:
        self.mem = SimpleNamespace(module_name="nba2k26.exe", hproc=None)

    def get_teams(self) -> list[str]:
        return []


class _RosterNavModelStub:
    def __init__(
        self,
        *,
        teams: list[str] | None = None,
        players_loaded: bool = False,
        teams_loaded: bool = False,
        players_dirty: bool = False,
        teams_dirty: bool = False,
    ) -> None:
        self.mem = SimpleNamespace(module_name="nba2k26.exe", hproc=object())
        self.players = [object()] if players_loaded else []
        source_teams = list(teams or ["Celtics", "Lakers"])
        self.team_list = list(enumerate(source_teams)) if teams_loaded else []
        self._dirty = {
            "players": players_dirty,
            "teams": teams_dirty,
        }
        self.refresh_players_calls = 0

    def is_dirty(self, entity: str) -> bool:
        return bool(self._dirty.get(str(entity or "").strip().lower(), False))

    def clear_dirty(self, *entities: str) -> None:
        for entity in entities:
            self._dirty[str(entity or "").strip().lower()] = False

    def get_teams(self) -> list[str]:
        return [name for _, name in self.team_list]

    def refresh_players(self) -> None:
        self.refresh_players_calls += 1
        if not self.team_list:
            self.team_list = [(0, "Celtics"), (1, "Lakers")]
        if not self.players:
            self.players = [object()]
        self.clear_dirty("players", "teams")


class _LegacyLeagueCategoryModelStub(_AppModelStub):
    def get_categories_for_super(self, super_type: str) -> dict[str, list[dict]]:
        if super_type == "League":
            return {
                "Hall of Famers": [],
                "Season Awards": [],
                "Career/Record Stats": [],
                "Season/Record Stats": [],
                "Single Game (Regular)/Basic Info": [],
            }
        return {}


def test_scan_thread_updates_ui_on_success() -> None:
    model = _ScanModelStub(teams=["Celtics", "Lakers"])
    app = _ScanAppStub(model)

    PlayerEditorApp._scan_thread(app)

    assert model.refresh_calls == 1
    assert app.scanning is False
    assert app.team_dropdown_updates == [["Celtics", "Lakers"]]
    assert app.player_refresh_calls == 1
    assert app.scan_status_var.get() == ""
    assert app.team_scan_status_var.get() == ""


def test_scan_thread_handles_refresh_failure_without_stalling() -> None:
    model = _ScanModelStub(raise_on_refresh=True)
    app = _ScanAppStub(model)

    PlayerEditorApp._scan_thread(app)

    # Regression guard: failed refresh should not leave the UI locked in scanning mode.
    assert app.scanning is False
    assert "failed" in str(app.scan_status_var.get()).lower()


def test_scan_teams_thread_handles_refresh_failure_without_stalling() -> None:
    model = _ScanModelStub(raise_on_refresh=True)
    app = _ScanAppStub(model)

    PlayerEditorApp._scan_teams_thread(app)

    # Regression guard: Teams refresh should fail gracefully and preserve retry flow.
    assert app.scanning is False
    assert "failed" in str(app.team_scan_status_var.get()).lower()


def test_trade_refresh_team_options_bootstraps_from_refresh() -> None:
    model = _TradeModelStub(team_list=[], refresh_result=[(5, "Bulls"), (1, "Celtics")])
    app = _TradeAppStub(model)

    PlayerEditorApp._trade_refresh_team_options(app)

    assert model.refresh_calls == 1
    assert app.trade_team_options == ["Celtics", "Bulls"]
    assert app.trade_team_lookup == {"Celtics": 1, "Bulls": 5}
    assert app.trade_participants == ["Celtics", "Bulls"]
    assert app.trade_active_team_var.get() == "Celtics"
    assert app.ensure_slot_calls == 1
    assert app.render_calls == 1


def test_show_nba_history_routes_to_history_page_and_refreshes() -> None:
    app = PlayerEditorApp(_AppModelStub())
    shown: list[str] = []
    refreshed: list[str] = []
    app._ensure_screen_built = lambda _key: None  # type: ignore[assignment]
    app._show_screen = lambda key: shown.append(key)  # type: ignore[assignment]
    app._refresh_league_records = lambda page_key="nba_history", *_args: refreshed.append(page_key)  # type: ignore[assignment]

    app.show_nba_history()

    assert shown == ["nba_history"]
    assert refreshed == ["nba_history"]


def test_show_nba_records_routes_to_records_page_and_refreshes() -> None:
    app = PlayerEditorApp(_AppModelStub())
    shown: list[str] = []
    refreshed: list[str] = []
    app._ensure_screen_built = lambda _key: None  # type: ignore[assignment]
    app._show_screen = lambda key: shown.append(key)  # type: ignore[assignment]
    app._refresh_league_records = lambda page_key="nba_history", *_args: refreshed.append(page_key)  # type: ignore[assignment]

    app.show_nba_records()

    assert shown == ["nba_records"]
    assert refreshed == ["nba_records"]


def test_show_league_alias_routes_to_nba_history_page() -> None:
    app = PlayerEditorApp(_AppModelStub())
    shown: list[str] = []
    refreshed: list[str] = []
    app._ensure_screen_built = lambda _key: None  # type: ignore[assignment]
    app._show_screen = lambda key: shown.append(key)  # type: ignore[assignment]
    app._refresh_league_records = lambda page_key="nba_history", *_args: refreshed.append(page_key)  # type: ignore[assignment]

    app.show_league()

    assert shown == ["nba_history"]
    assert refreshed == ["nba_history"]


def test_ensure_league_categories_splits_legacy_league_supertype() -> None:
    app = PlayerEditorApp(_LegacyLeagueCategoryModelStub())

    app._ensure_league_categories("nba_records")
    app._ensure_league_categories("nba_history")
    records_state = app._league_state("nba_records")
    history_state = app._league_state("nba_history")

    assert set(records_state["categories"]) == {
        "Career/Record Stats",
        "Season/Record Stats",
        "Single Game (Regular)/Basic Info",
    }
    assert set(history_state["categories"]) == {"Hall of Famers", "Season Awards"}


def test_start_scan_uses_shared_scan_flow() -> None:
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


def test_start_team_scan_applies_pending_selection_via_shared_flow() -> None:
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


def test_build_ui_does_not_trigger_roster_refresh_on_startup(monkeypatch) -> None:
    class _BuildModel:
        def __init__(self) -> None:
            self.mem = SimpleNamespace(module_name="nba2k26.exe", hproc=None)
            self.refresh_players_calls = 0
            self.team_list: list[tuple[int, str]] = []
            self.players: list[object] = []

        def get_teams(self) -> list[str]:
            return []

        def refresh_players(self) -> None:
            self.refresh_players_calls += 1

    model = _BuildModel()
    app = PlayerEditorApp(model)  # type: ignore[arg-type]

    def _fake_build_home(app_inst) -> None:
        app_inst.screen_tags["home"] = "screen_home"

    monkeypatch.setattr(app_module, "build_home_screen", _fake_build_home)
    dpg.create_context()
    try:
        app.build_ui()
    finally:
        dpg.destroy_context()

    assert model.refresh_players_calls == 0


def test_all_non_home_screens_are_lazy_built_once(monkeypatch) -> None:
    counts: dict[str, int] = {}

    def _make_builder(key: str):
        def _builder(app_inst) -> None:
            counts[key] = counts.get(key, 0) + 1
            app_inst.screen_tags[key] = f"screen_{key}"

        return _builder

    monkeypatch.setattr(app_module, "build_players_screen", _make_builder("players"))
    monkeypatch.setattr(app_module, "build_teams_screen", _make_builder("teams"))
    monkeypatch.setattr(app_module, "build_nba_history_screen", _make_builder("nba_history"))
    monkeypatch.setattr(app_module, "build_nba_records_screen", _make_builder("nba_records"))
    monkeypatch.setattr(app_module, "build_staff_screen", _make_builder("staff"))
    monkeypatch.setattr(app_module, "build_stadium_screen", _make_builder("stadium"))
    monkeypatch.setattr(app_module, "build_excel_screen", _make_builder("excel"))
    monkeypatch.setattr(app_module, "build_trade_players_screen", _make_builder("trade"))

    app = PlayerEditorApp(_AppModelStub())
    app._show_screen = lambda _key: None  # type: ignore[assignment]
    app._ensure_roster_loaded = lambda **_kwargs: None  # type: ignore[assignment]
    app._refresh_league_records = lambda *_args, **_kwargs: None  # type: ignore[assignment]
    app._refresh_trade_data = lambda: None  # type: ignore[assignment]
    app._refresh_staff_list = lambda: None  # type: ignore[assignment]
    app._refresh_stadium_list = lambda: None  # type: ignore[assignment]

    app.show_players()
    app.show_players()
    app.show_teams()
    app.show_teams()
    app.show_nba_history()
    app.show_nba_history()
    app.show_nba_records()
    app.show_nba_records()
    app.show_staff()
    app.show_staff()
    app.show_stadium()
    app.show_stadium()
    app.show_excel()
    app.show_excel()
    app.show_trade_players()
    app.show_trade_players()

    assert counts == {
        "players": 1,
        "teams": 1,
        "nba_history": 1,
        "nba_records": 1,
        "staff": 1,
        "stadium": 1,
        "excel": 1,
        "trade": 1,
    }


def test_navigation_players_teams_players_reuses_loaded_roster(monkeypatch) -> None:
    model = _RosterNavModelStub(
        players_loaded=False,
        teams_loaded=False,
        players_dirty=False,
        teams_dirty=False,
    )
    app = PlayerEditorApp(model)  # type: ignore[arg-type]
    app._show_screen = lambda _key: None  # type: ignore[assignment]
    app._ensure_screen_built = lambda _key: None  # type: ignore[assignment]
    app._update_team_dropdown = lambda _teams: None  # type: ignore[assignment]
    app._refresh_player_list = lambda: None  # type: ignore[assignment]

    start_calls = 0

    def _fake_start_roster_scan(self, *, apply_pending_team_select: bool) -> None:
        nonlocal start_calls
        del apply_pending_team_select
        start_calls += 1
        self.model.refresh_players()

    monkeypatch.setattr(PlayerEditorApp, "_start_roster_scan", _fake_start_roster_scan)

    app.show_players()
    app.show_teams()
    app.show_players()

    assert start_calls == 1
    assert model.refresh_players_calls == 1
