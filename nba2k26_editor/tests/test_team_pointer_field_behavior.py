from __future__ import annotations

from types import SimpleNamespace

from nba2k26_editor.models import data_model as data_model_mod
from nba2k26_editor.models.data_model import PlayerDataModel


def test_decode_team_pointer_field_displays_team_name(monkeypatch) -> None:
    monkeypatch.setattr(data_model_mod, "TEAM_STRIDE", 32, raising=False)

    model = PlayerDataModel.__new__(PlayerDataModel)
    model.team_list = [(3, "Lakers")]
    model._resolve_team_base_ptr = lambda: 0x1000  # type: ignore[method-assign]

    pointer = 0x1000 + (3 * 32)
    buf = bytearray(160)
    buf[96:104] = int(pointer).to_bytes(8, "little")

    value = PlayerDataModel.decode_field_value_from_buffer(
        model,
        entity_type="player",
        entity_index=0,
        category="Pointers",
        field_name="Current Team Address",
        meta={"offset": 96, "length": 64, "startBit": 0, "type": "Pointer"},
        record_buffer=buf,
    )

    assert value == "Lakers"


def test_decode_non_team_pointer_field_stays_hex(monkeypatch) -> None:
    monkeypatch.setattr(data_model_mod, "TEAM_STRIDE", 32, raising=False)

    model = PlayerDataModel.__new__(PlayerDataModel)
    model.team_list = [(3, "Lakers")]
    model._resolve_team_base_ptr = lambda: 0x1000  # type: ignore[method-assign]

    pointer = 0x1000 + (3 * 32)
    buf = bytearray(160)
    buf[96:104] = int(pointer).to_bytes(8, "little")

    value = PlayerDataModel.decode_field_value_from_buffer(
        model,
        entity_type="player",
        entity_index=0,
        category="Pointers",
        field_name="Body Address",
        meta={"offset": 96, "length": 64, "startBit": 0, "type": "Pointer"},
        record_buffer=buf,
    )

    assert value == "0x0000000000001060"


def test_encode_team_pointer_field_accepts_team_name(monkeypatch) -> None:
    monkeypatch.setattr(data_model_mod, "TEAM_STRIDE", 32, raising=False)

    model = PlayerDataModel.__new__(PlayerDataModel)
    model.mem = SimpleNamespace(open_process=lambda: True)
    model.team_list = [(3, "Lakers")]
    model._resolve_team_base_ptr = lambda: 0x1000  # type: ignore[method-assign]

    captured: dict[str, int] = {}

    def _capture_write(
        _entity_type: str,
        _entity_index: int,
        _offset: int,
        _start_bit: int,
        _length_bits: int,
        value: object,
        **_kwargs,
    ) -> bool:
        captured["value"] = int(value)
        return True

    model._write_entity_field_typed = _capture_write  # type: ignore[method-assign]

    ok = PlayerDataModel.encode_field_value(
        model,
        entity_type="player",
        entity_index=0,
        category="Pointers",
        field_name="Current Team Address",
        meta={"offset": 96, "length": 64, "startBit": 0, "type": "Pointer"},
        display_value="Lakers",
    )

    assert ok is True
    assert captured["value"] == 0x1060

