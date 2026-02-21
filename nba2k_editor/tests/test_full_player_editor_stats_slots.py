from __future__ import annotations

import sys
import types
from typing import Any

# Allow importing FullPlayerEditor in environments where Dear PyGui is not installed.
sys.modules.setdefault("dearpygui", types.ModuleType("dearpygui"))
sys.modules.setdefault("dearpygui.dearpygui", types.ModuleType("dearpygui.dearpygui"))

from nba2k_editor.models.player import Player
from nba2k_editor.models.schema import FieldMetadata
from nba2k_editor.ui import full_player_editor as full_player_editor_mod
from nba2k_editor.ui.full_player_editor import FullPlayerEditor


def test_prepare_stats_tabs_keeps_career_and_season_awards_merge() -> None:
    categories = {
        "Stats - Career": [{"name": "Points#Career", "offset": 1}],
        "Stats - Season": [{"name": "Points#Season", "offset": 2}],
        "Stats - Awards": [{"name": "Most Valuable Player", "offset": 3}],
    }

    prepared = FullPlayerEditor._prepare_stats_tabs(categories)

    assert "Career Stats" in prepared
    assert "Season Stats" in prepared
    assert "Stats - Awards" not in prepared

    career_names = [str(field.get("name")) for field in prepared["Career Stats"]]
    season_names = [str(field.get("name")) for field in prepared["Season Stats"]]
    assert "Points#Career" in career_names
    assert "Points#Season" in season_names
    assert "Most Valuable Player" in career_names
    assert "Most Valuable Player" in season_names


def test_prepare_stats_tabs_adds_season_slot_selector_and_hides_stats_ids() -> None:
    categories = {
        "Stats - IDs": [
            {"name": "STATS_ID#2", "normalized_name": "STATSID2", "offset": 12},
            {"name": "Current Year Stat ID", "normalized_name": "CURRENTYEARSTATID", "offset": 10},
            {"name": "STATS_ID#1", "normalized_name": "STATSID1", "offset": 11},
        ],
        "Stats - Season": [{"name": "Points#Season", "offset": 20}],
    }

    prepared = FullPlayerEditor._prepare_stats_tabs(categories)

    assert "Stats - IDs" not in prepared
    assert "Season Stats" in prepared

    season_fields = prepared["Season Stats"]
    selector = season_fields[0]
    assert selector.get("__season_slot_selector") is True
    assert selector.get("__source_category") == "Stats - IDs"
    assert selector.get("values") == ["0 - Current Season", "1", "2"]

    slot_defs = selector.get("__season_slot_defs")
    assert isinstance(slot_defs, list)
    assert [int(item.get("slot", -1)) for item in slot_defs] == [0, 1, 2]
    assert [str(item.get("field_name") or "") for item in slot_defs] == [
        "Current Year Stat ID",
        "STATS_ID#1",
        "STATS_ID#2",
    ]


def test_load_all_values_async_routes_maxey_season_and_awards_fields_via_selected_slot() -> None:
    # Tyrese Maxey (player index 0) 24-25 row values from the in-game table capture.
    maxey_values: list[tuple[str, str, int]] = [
        ("Points#Season", "Stats - Season", 1369),
        ("Rebounds#Season", "Stats - Season", 174),
        ("Assists#Season", "Stats - Season", 317),
        ("Steals#Season", "Stats - Season", 91),
        ("Blocks#Season", "Stats - Season", 21),
        ("Field Goals Made#Season", "Stats - Season", 477),
        ("Field Goals Attempted#Season", "Stats - Season", 1091),
        ("Three Pointers Made#Season", "Stats - Season", 161),
        ("Three Pointers Attempted#Season", "Stats - Season", 478),
        ("Free Throws Made#Season", "Stats - Season", 254),
        ("Free Throws Attempted#Season", "Stats - Season", 289),
        ("Minutes Played#Season", "Stats - Season", 1960),
        ("Games Started", "Stats - Awards", 52),
        ("Games Played", "Stats - Awards", 52),
        ("Fouls", "Stats - Awards", 116),
        ("Turnovers", "Stats - Awards", 124),
        ("Double Doubles", "Stats - Awards", 8),
        ("Triple Doubles", "Stats - Awards", 1),
        ("Total +/-", "Stats - Awards", -124),
    ]

    player_record_ptr = 0x1000
    season_record_ptr = 0x9000
    expected_by_name = {name: value for name, _source, value in maxey_values}
    expected_by_key = {("Season Stats", name): value for name, _source, value in maxey_values}

    class _ModelStub:
        def __init__(self) -> None:
            self.calls: list[dict[str, Any]] = []

        def decode_field_value(
            self,
            *,
            entity_type: str,
            entity_index: int,
            category: str,
            field_name: str,
            meta: FieldMetadata,
            record_ptr: int | None = None,
        ) -> object | None:
            del entity_type, entity_index, category, meta
            self.calls.append({"field_name": field_name, "record_ptr": record_ptr})
            if record_ptr != season_record_ptr:
                return None
            return expected_by_name.get(field_name)

    editor = FullPlayerEditor.__new__(FullPlayerEditor)
    editor.model = _ModelStub()
    editor.player = Player(index=0, first_name="Tyrese", last_name="Maxey", record_ptr=player_record_ptr)
    editor.field_vars = {
        "Season Stats": {
            name: f"control_{idx}"
            for idx, (name, _source, _value) in enumerate(maxey_values)
        }
    }
    editor.field_meta = {
        ("Season Stats", name): FieldMetadata(offset=0, start_bit=0, length=32)
        for name, _source, _value in maxey_values
    }
    editor.field_source_category = {
        ("Season Stats", name): source
        for name, source, _value in maxey_values
    }
    editor._season_slot_selector_key = None
    editor._loading_values = False
    editor._closed = False
    editor._resolve_selected_season_record_ptr = lambda _player=None: season_record_ptr  # type: ignore[assignment]

    captured: dict[tuple[str, str], object] = {}
    editor._apply_loaded_values = lambda values: captured.update(values)  # type: ignore[assignment]

    editor._load_all_values_async()

    assert captured == expected_by_key
    assert all(call["record_ptr"] == season_record_ptr for call in editor.model.calls)


def test_season_slot_change_switches_loaded_values_per_year() -> None:
    class _DPGStub:
        def __init__(self) -> None:
            self.values: dict[str, object] = {}

        def does_item_exist(self, _item: object) -> bool:
            return True

        def get_value(self, item: object) -> object:
            return self.values.get(str(item), "")

        def set_value(self, item: object, value: object) -> None:
            self.values[str(item)] = value

    dpg_stub = _DPGStub()
    full_player_editor_mod.dpg = dpg_stub  # type: ignore[assignment]

    season_base_ptr = 0x9000
    season_stride = 0x100
    field_sources: list[tuple[str, str]] = [
        ("Points#Season", "Stats - Season"),
        ("Rebounds#Season", "Stats - Season"),
        ("Assists#Season", "Stats - Season"),
        ("Steals#Season", "Stats - Season"),
        ("Blocks#Season", "Stats - Season"),
        ("Field Goals Made#Season", "Stats - Season"),
        ("Field Goals Attempted#Season", "Stats - Season"),
        ("Three Pointers Made#Season", "Stats - Season"),
        ("Three Pointers Attempted#Season", "Stats - Season"),
        ("Free Throws Made#Season", "Stats - Season"),
        ("Free Throws Attempted#Season", "Stats - Season"),
        ("Minutes Played#Season", "Stats - Season"),
        ("Turnovers", "Stats - Awards"),
        ("Fouls", "Stats - Awards"),
        ("Games Started", "Stats - Awards"),
        ("Games Played", "Stats - Awards"),
        ("Double Doubles", "Stats - Awards"),
        ("Triple Doubles", "Stats - Awards"),
        ("Total +/-", "Stats - Awards"),
    ]

    # Tyrese Maxey rows from the provided in-game table (24-25 to 20-21).
    season_values_by_ptr = {
        season_base_ptr + 0 * season_stride: {
            "Points#Season": 1369,
            "Rebounds#Season": 174,
            "Assists#Season": 317,
            "Steals#Season": 91,
            "Blocks#Season": 21,
            "Turnovers": 124,
            "Field Goals Made#Season": 477,
            "Field Goals Attempted#Season": 1091,
            "Three Pointers Made#Season": 161,
            "Three Pointers Attempted#Season": 478,
            "Free Throws Made#Season": 254,
            "Free Throws Attempted#Season": 289,
            "Minutes Played#Season": 1960,
            "Fouls": 116,
            "Games Started": 52,
            "Games Played": 52,
            "Double Doubles": 8,
            "Triple Doubles": 1,
            "Total +/-": -124,
        },
        season_base_ptr + 1 * season_stride: {
            "Points#Season": 1816,
            "Rebounds#Season": 258,
            "Assists#Season": 433,
            "Steals#Season": 69,
            "Blocks#Season": 33,
            "Turnovers": 116,
            "Field Goals Made#Season": 638,
            "Field Goals Attempted#Season": 1419,
            "Three Pointers Made#Season": 212,
            "Three Pointers Attempted#Season": 569,
            "Free Throws Made#Season": 328,
            "Free Throws Attempted#Season": 378,
            "Minutes Played#Season": 2626,
            "Fouls": 151,
            "Games Started": 70,
            "Games Played": 70,
            "Double Doubles": 9,
            "Triple Doubles": 0,
            "Total +/-": 303,
        },
        season_base_ptr + 2 * season_stride: {
            "Points#Season": 1218,
            "Rebounds#Season": 176,
            "Assists#Season": 212,
            "Steals#Season": 49,
            "Blocks#Season": 8,
            "Turnovers": 80,
            "Field Goals Made#Season": 439,
            "Field Goals Attempted#Season": 913,
            "Three Pointers Made#Season": 160,
            "Three Pointers Attempted#Season": 369,
            "Free Throws Made#Season": 180,
            "Free Throws Attempted#Season": 213,
            "Minutes Played#Season": 2016,
            "Fouls": 132,
            "Games Started": 41,
            "Games Played": 60,
            "Double Doubles": 0,
            "Triple Doubles": 0,
            "Total +/-": 241,
        },
        season_base_ptr + 3 * season_stride: {
            "Points#Season": 1311,
            "Rebounds#Season": 240,
            "Assists#Season": 321,
            "Steals#Season": 55,
            "Blocks#Season": 32,
            "Turnovers": 88,
            "Field Goals Made#Season": 483,
            "Field Goals Attempted#Season": 995,
            "Three Pointers Made#Season": 132,
            "Three Pointers Attempted#Season": 309,
            "Free Throws Made#Season": 213,
            "Free Throws Attempted#Season": 246,
            "Minutes Played#Season": 2650,
            "Fouls": 156,
            "Games Started": 74,
            "Games Played": 75,
            "Double Doubles": 1,
            "Triple Doubles": 0,
            "Total +/-": 192,
        },
        season_base_ptr + 4 * season_stride: {
            "Points#Season": 488,
            "Rebounds#Season": 104,
            "Assists#Season": 120,
            "Steals#Season": 26,
            "Blocks#Season": 13,
            "Turnovers": 41,
            "Field Goals Made#Season": 198,
            "Field Goals Attempted#Season": 429,
            "Three Pointers Made#Season": 31,
            "Three Pointers Attempted#Season": 103,
            "Free Throws Made#Season": 61,
            "Free Throws Attempted#Season": 70,
            "Minutes Played#Season": 936,
            "Fouls": 79,
            "Games Started": 8,
            "Games Played": 61,
            "Double Doubles": 0,
            "Triple Doubles": 0,
            "Total +/-": -52,
        },
    }

    class _ModelStub:
        def _league_pointer_meta(self, pointer_key: str) -> tuple[list[dict[str, object]], int]:
            if pointer_key == "career_stats":
                return ([{"rva": 1}], season_stride)
            return ([], 0)

        def _league_pointer_for_category(self, category_name: str) -> tuple[str, list[dict[str, object]], int, int]:
            del category_name
            return ("NBAHistory", [{"rva": 1}], season_stride, 200)

        def _resolve_league_base(self, pointer_key: str, chains: list[dict[str, object]], validator=None) -> int:
            del pointer_key, chains, validator
            return season_base_ptr

        def decode_field_value(
            self,
            *,
            entity_type: str,
            entity_index: int,
            category: str,
            field_name: str,
            meta: FieldMetadata,
            record_ptr: int | None = None,
        ) -> object | None:
            del entity_type, entity_index, meta
            if category == "Stats - IDs":
                if field_name == "Current Year Stat ID":
                    return 0
                if field_name == "STATS_ID#1":
                    return 1
                if field_name == "STATS_ID#2":
                    return 2
                if field_name == "STATS_ID#3":
                    return 3
                if field_name == "STATS_ID#4":
                    return 4
                return -1
            if category in {"Stats - Season", "Stats - Awards"}:
                return season_values_by_ptr.get(record_ptr, {}).get(field_name)
            return None

    editor = FullPlayerEditor.__new__(FullPlayerEditor)
    editor.model = _ModelStub()
    editor.player = Player(index=0, first_name="Tyrese", last_name="Maxey", record_ptr=0x1000)
    editor._season_slot_selector_key = ("Season Stats", "Season Stat Slot")
    editor._season_slot_defs = [
        {"slot": 0, "label": "0 - Current Season", "field_name": "Current Year Stat ID", "source_category": "Stats - IDs", "meta": {}},
        {"slot": 1, "label": "1", "field_name": "STATS_ID#1", "source_category": "Stats - IDs", "meta": {}},
        {"slot": 2, "label": "2", "field_name": "STATS_ID#2", "source_category": "Stats - IDs", "meta": {}},
        {"slot": 3, "label": "3", "field_name": "STATS_ID#3", "source_category": "Stats - IDs", "meta": {}},
        {"slot": 4, "label": "4", "field_name": "STATS_ID#4", "source_category": "Stats - IDs", "meta": {}},
    ]
    editor._season_stat_field_keys = [("Season Stats", name) for name, _source in field_sources]
    editor.field_vars = {
        "Season Stats": {
            "Season Stat Slot": "slot_ctrl",
            **{
                name: f"ctrl_{idx}"
                for idx, (name, _source) in enumerate(field_sources)
            },
        }
    }
    editor.field_meta = {
        ("Season Stats", name): FieldMetadata(offset=0, start_bit=0, length=32)
        for name, _source in field_sources
    }
    editor.field_source_category = {
        ("Season Stats", name): source
        for name, source in field_sources
    }
    editor._loading_values = False
    editor._closed = False

    captured: dict[tuple[str, str], object] = {}
    editor._apply_loaded_values = lambda values: captured.update(values)  # type: ignore[assignment]

    slot_labels = ["0 - Current Season", "1", "2", "3", "4"]
    for slot_idx, label in enumerate(slot_labels):
        dpg_stub.values["slot_ctrl"] = label
        captured.clear()
        editor._on_season_slot_changed()
        expected = season_values_by_ptr[season_base_ptr + slot_idx * season_stride]
        assert captured == {("Season Stats", name): value for name, value in expected.items()}


def test_season_stats_base_prefers_career_stats_pointer_when_available() -> None:
    calls: list[str] = []

    class _ModelStub:
        def _league_pointer_meta(self, pointer_key: str) -> tuple[list[dict[str, object]], int]:
            calls.append(f"meta:{pointer_key}")
            if pointer_key == "career_stats":
                return ([{"rva": 1}], 64)
            return ([], 0)

        def _resolve_league_base(self, pointer_key: str, chains: list[dict[str, object]], validator=None) -> int | None:
            del chains, validator
            calls.append(f"base:{pointer_key}")
            if pointer_key == "career_stats":
                return 0x7000
            return None

    editor = FullPlayerEditor.__new__(FullPlayerEditor)
    editor.model = _ModelStub()

    base_ptr, stride = editor._season_stats_base_and_stride()

    assert (base_ptr, stride) == (0x7000, 64)
    assert calls == ["meta:career_stats", "base:career_stats"]


def test_season_stats_base_requires_career_stats_pointer_metadata() -> None:
    calls: list[str] = []

    class _ModelStub:
        def _league_pointer_meta(self, pointer_key: str) -> tuple[list[dict[str, object]], int]:
            calls.append(f"meta:{pointer_key}")
            return ([], 0)

        def _resolve_league_base(self, pointer_key: str, chains: list[dict[str, object]], validator=None) -> int | None:
            del chains, validator
            calls.append(f"base:{pointer_key}")
            return None

    editor = FullPlayerEditor.__new__(FullPlayerEditor)
    editor.model = _ModelStub()

    base_ptr, stride = editor._season_stats_base_and_stride()

    assert (base_ptr, stride) == (None, 0)
    assert calls == ["meta:career_stats"]