from __future__ import annotations

from types import SimpleNamespace

import pytest

pytest.importorskip("dearpygui.dearpygui")

from nba2k_editor.entrypoints import full_editor


class _MemStub:
    def __init__(self, open_ok: bool = True) -> None:
        self._open_ok = open_ok
        self.hproc = object() if open_ok else None

    def open_process(self) -> bool:
        self.hproc = object() if self._open_ok else None
        return self._open_ok


class _ModelStub:
    def __init__(self, open_ok: bool = True) -> None:
        self.mem = _MemStub(open_ok=open_ok)
        self.players = [SimpleNamespace(index=1), SimpleNamespace(index=7)]
        self.team_list = [(3, "Bulls")]
        self.refresh_players_calls = 0

    def refresh_players(self) -> None:
        self.refresh_players_calls += 1


def test_parse_editor_request_player_indices() -> None:
    request = full_editor.parse_editor_request(["--editor", "player", "--indices", "1,7,1"])

    assert request.editor == "player"
    assert request.indices == (1, 7)
    assert request.index is None


def test_parse_editor_request_requires_index_for_team() -> None:
    with pytest.raises(SystemExit):
        full_editor.parse_editor_request(["--editor", "team"])


def test_open_requested_editor_routes_player(monkeypatch) -> None:
    model = _ModelStub(open_ok=True)
    host = full_editor._ChildEditorHost(model)  # type: ignore[attr-defined]
    calls: list[tuple[object, tuple[int, ...]]] = []

    def _fake_player_editor(app, players, _model):
        del _model
        calls.append((app, tuple(getattr(player, "index", -1) for player in players)))

    monkeypatch.setattr(full_editor, "FullPlayerEditor", _fake_player_editor)

    ok = full_editor._open_requested_editor(host, full_editor.EditorRequest(editor="player", indices=(1, 7)))

    assert ok is True
    assert calls == [(host, (1, 7))]


def test_open_requested_editor_routes_team(monkeypatch) -> None:
    model = _ModelStub(open_ok=True)
    host = full_editor._ChildEditorHost(model)  # type: ignore[attr-defined]
    calls: list[tuple[int, str]] = []

    def _fake_team_editor(_app, team_idx, team_name, _model):
        del _app, _model
        calls.append((team_idx, team_name))

    monkeypatch.setattr(full_editor, "FullTeamEditor", _fake_team_editor)

    ok = full_editor._open_requested_editor(host, full_editor.EditorRequest(editor="team", index=3))

    assert ok is True
    assert calls == [(3, "Bulls")]