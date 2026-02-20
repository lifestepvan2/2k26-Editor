from __future__ import annotations

from nba2k_editor.models.services.io_codec import FieldSpec, IOCodec
from nba2k_editor.models.services.player_service import PlayerService
from nba2k_editor.models.services.team_service import TeamService


class _StubModel:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []
        self.dirty: set[str] = set()

    def mark_dirty(self, *entities: str) -> None:
        for e in entities:
            self.dirty.add(e)

    def get_field_value_typed(self, *args, **kwargs):
        self.calls.append(("get_player", args, kwargs))
        return 77

    def set_field_value_typed(self, *args, **kwargs):
        self.calls.append(("set_player", args, kwargs))
        return True

    def get_team_field_value_typed(self, *args, **kwargs):
        self.calls.append(("get_team", args, kwargs))
        return 88

    def set_team_field_value_typed(self, *args, **kwargs):
        self.calls.append(("set_team", args, kwargs))
        return True

    def get_team_fields(self, team_index: int):
        self.calls.append(("get_team_fields", (team_index,), {}))
        return {"Team Name": "Lakers"}

    def set_team_fields(self, team_index: int, values: dict[str, str]) -> bool:
        self.calls.append(("set_team_fields", (team_index, values), {}))
        return True

    def refresh_players(self) -> None:
        self.calls.append(("refresh_players", (), {}))


def test_io_codec_routes_player_and_team_calls():
    model = _StubModel()
    codec = IOCodec(model)
    spec = FieldSpec(offset=4, start_bit=0, length=8, field_type="Integer")
    assert codec.get_player(1, spec) == 77
    assert codec.get_team(2, spec) == 88
    assert codec.set_player(1, spec, 55)
    assert codec.set_team(2, spec, 66)
    names = [name for name, _args, _kwargs in model.calls]
    assert "get_player" in names
    assert "get_team" in names
    assert "set_player" in names
    assert "set_team" in names


def test_services_mark_dirty_on_writes():
    model = _StubModel()
    spec = FieldSpec(offset=4, start_bit=0, length=8)
    player_service = PlayerService(model)
    team_service = TeamService(model)
    assert player_service.set_field(1, spec, 10)
    assert "players" in model.dirty
    assert team_service.set_field(1, spec, 10)
    assert "teams" in model.dirty
    assert team_service.set_fields(1, {"Team Name": "Knicks"})
    assert "teams" in model.dirty

