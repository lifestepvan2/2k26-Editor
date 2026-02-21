"""Player entity service."""
from __future__ import annotations

from typing import Any

from .io_codec import FieldSpec, IOCodec


class PlayerService:
    def __init__(self, model: Any, codec: IOCodec | None = None) -> None:
        self.model = model
        self.codec = codec or IOCodec(model)

    def refresh(self) -> None:
        self.model.refresh_players()

    def get_field(self, player_index: int, spec: FieldSpec) -> object | None:
        return self.codec.get_player(player_index, spec)

    def set_field(self, player_index: int, spec: FieldSpec, value: object, *, deref_cache: dict[int, int] | None = None) -> bool:
        ok = self.codec.set_player(player_index, spec, value, deref_cache=deref_cache)
        if ok and hasattr(self.model, "mark_dirty"):
            self.model.mark_dirty("players")
        return ok

