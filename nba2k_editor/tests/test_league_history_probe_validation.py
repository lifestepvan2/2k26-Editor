from __future__ import annotations

from nba2k_editor.models.data_model import PlayerDataModel


def test_get_league_records_accepts_base_when_first_row_is_blank_but_next_row_has_data() -> None:
    class _MemStub:
        def __init__(self) -> None:
            self.hproc = object()

        def open_process(self) -> bool:
            return True

        def read_bytes(self, _addr: int, size: int) -> bytes:
            return b"\x00" * size

    model = PlayerDataModel.__new__(PlayerDataModel)
    model.mem = _MemStub()
    model._league_pointer_cache = {}
    model._resolved_league_bases = {}
    model.get_league_categories = lambda: {  # type: ignore[method-assign]
        "Season Awards": [
            {
                "name": "Player Name",
                "type": "wstring",
                "offset": 0,
                "startBit": 0,
                "length": 16,
            }
        ]
    }
    model._league_pointer_for_category = lambda _category_name: ("NBAHistory", [{"rva": 1}], 16, 3)  # type: ignore[method-assign]

    def _resolve_league_base(pointer_key: str, chains: list[dict[str, object]], validator=None) -> int | None:
        del pointer_key, chains
        assert validator is not None
        assert validator(0x1000) is True
        return 0x1000

    model._resolve_league_base = _resolve_league_base  # type: ignore[method-assign]

    def _decode_field_value_from_buffer(
        *,
        entity_type: str,
        entity_index: int,
        category: str,
        field_name: str,
        meta: dict[str, object],
        record_buffer: bytes | bytearray | memoryview,
        record_addr: int | None = None,
        record_ptr: int | None = None,
        enum_as_label: bool = False,
    ) -> object | None:
        del entity_type, category, field_name, meta, record_buffer, record_addr, record_ptr, enum_as_label
        if entity_index == 0:
            return ""
        if entity_index == 1:
            return "Tyrese Maxey"
        return ""

    model.decode_field_value_from_buffer = _decode_field_value_from_buffer  # type: ignore[method-assign]

    records = PlayerDataModel.get_league_records(model, "Season Awards", max_records=3)

    assert len(records) == 1
    assert records[0]["_index"] == 1
    assert records[0]["Player Name"] == "Tyrese Maxey"