from gm_rl.actions import GMTransaction
from gm_rl.adapters.editor_live import EditorLiveAdapter
from nba2k_editor.models.player import Player


class _StubMem:
    def __init__(self) -> None:
        self.hproc = True
        self.base_addr = 0x1000
        self.module_name = "stub.exe"

    def open_process(self) -> bool:  # pragma: no cover - trivial
        return True


class _StubModel:
    def __init__(self) -> None:
        self.mem = _StubMem()
        self.players = [
            Player(0, "A", "One", "Team A", 1, record_ptr=0x2000),
            Player(1, "B", "Two", "Team A", 1, record_ptr=0x2100),
            Player(2, "C", "Three", "Team B", 2, record_ptr=0x2200),
        ]
        self.team_list = [(1, "Team A"), (2, "Team B")]

    def refresh_players(self) -> None:
        return None

    def _build_team_list_from_players(self, players):
        return list(self.team_list)


def test_live_adapter_builds_roster_from_stub():
    adapter = EditorLiveAdapter(model=_StubModel(), dry_run=True)
    state = adapter.load_roster_state(seed=123)
    assert len(state.players) == 3
    assert set(state.teams[1].roster) == {0, 1}
    assert state.teams[2].roster == [2]


def test_rotation_minutes_cap_enforced():
    adapter = EditorLiveAdapter(model=_StubModel(), dry_run=True)
    state = adapter.load_roster_state(seed=1)
    minutes = {pid: 60.0 for pid in state.teams[1].roster}
    result = adapter.apply_gm_action(GMTransaction(head="rotation", payload={"team_id": 1, "minutes": minutes}))
    assert "rotation_rejected_minutes_cap" in result.metadata


def test_trade_swaps_rosters():
    adapter = EditorLiveAdapter(model=_StubModel(), dry_run=True)
    adapter.load_roster_state(seed=5)
    result = adapter.apply_gm_action(
        GMTransaction(head="trade", payload={"team_id": 1, "target_player_id": 2, "secondary_player_id": 0, "accept": True})
    )
    state = result.new_state
    assert state.players[2].team_id == 1
    assert state.players[0].team_id == 2
    assert 2 in state.teams[1].roster
    assert 0 in state.teams[2].roster
