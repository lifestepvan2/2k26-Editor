"""Team entity service."""
from __future__ import annotations

from typing import Any

from .io_codec import FieldSpec, IOCodec


class TeamService:
    def __init__(self, model: Any, codec: IOCodec | None = None) -> None:
        self.model = model
        self.codec = codec or IOCodec(model)

    def refresh(self) -> None:
        self.model.refresh_players()

    def get_fields(self, team_index: int) -> dict[str, str] | None:
        return self.model.get_team_fields(team_index)

    def set_fields(self, team_index: int, values: dict[str, str]) -> bool:
        ok = self.model.set_team_fields(team_index, values)
        if ok and hasattr(self.model, "mark_dirty"):
            self.model.mark_dirty("teams")
        return ok

    def get_field(self, team_index: int, spec: FieldSpec) -> object | None:
        return self.codec.get_team(team_index, spec)

    def set_field(self, team_index: int, spec: FieldSpec, value: object, *, deref_cache: dict[int, int] | None = None) -> bool:
        ok = self.codec.set_team(team_index, spec, value, deref_cache=deref_cache)
        if ok and hasattr(self.model, "mark_dirty"):
            self.model.mark_dirty("teams")
        return ok

