"""Resolution helpers for merged offsets payloads."""
from __future__ import annotations

from typing import Any, Callable


class OffsetResolveError(RuntimeError):
    """Raised when an offsets payload cannot be resolved."""


class OffsetResolver:
    def __init__(
        self,
        convert_schema: Callable[[object, str | None], dict[str, Any] | None],
        select_entry: Callable[[object, str | None], dict[str, Any] | None],
    ) -> None:
        self._convert_schema = convert_schema
        self._select_entry = select_entry

    def resolve(self, raw: object, target_executable: str | None = None) -> dict[str, Any] | None:
        converted = self._convert_schema(raw, target_executable)
        if converted is not None:
            return converted
        selected = self._select_entry(raw, target_executable)
        if selected and selected is not raw:
            selected_converted = self._convert_schema(selected, target_executable)
            return selected_converted or selected
        if isinstance(raw, dict):
            return raw
        return None

    def require_dict(self, raw: object, target_executable: str | None = None) -> dict[str, Any]:
        resolved = self.resolve(raw, target_executable)
        if not isinstance(resolved, dict):
            target = target_executable or "unknown target"
            raise OffsetResolveError(f"Could not resolve offsets payload for {target}.")
        return resolved

