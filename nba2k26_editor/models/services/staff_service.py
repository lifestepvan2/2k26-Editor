"""Staff entity service."""
from __future__ import annotations

from typing import Any

from .io_codec import FieldSpec, IOCodec


class StaffService:
    def __init__(self, model: Any, codec: IOCodec | None = None) -> None:
        self.model = model
        self.codec = codec or IOCodec(model)

    def refresh(self) -> list[tuple[int, str]]:
        return self.model.refresh_staff()

    def get_field(self, staff_index: int, spec: FieldSpec) -> object | None:
        return self.codec.get_staff(staff_index, spec)

    def set_field(self, staff_index: int, spec: FieldSpec, value: object, *, deref_cache: dict[int, int] | None = None) -> bool:
        ok = self.codec.set_staff(staff_index, spec, value, deref_cache=deref_cache)
        if ok and hasattr(self.model, "mark_dirty"):
            self.model.mark_dirty("staff")
        return ok

