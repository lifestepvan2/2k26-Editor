from __future__ import annotations

import os
import sys
import importlib

import pytest

from nba2k_editor.core.config import MODULE_NAME
from nba2k_editor.core.offsets import MAX_PLAYERS, initialize_offsets
from nba2k_editor.memory.game_memory import GameMemory
from nba2k_editor.models.data_model import PlayerDataModel
from nba2k_editor.models.player import Player
from nba2k_editor.models.schema import FieldMetadata

_ID_FIELD_NAMES = [
    "Current Year Stat ID",
    "STATS_ID#1",
    "STATS_ID#2",
    "STATS_ID#3",
    "STATS_ID#4",
]

_SEASON_FIELDS = [
    "Points#Season",
    "Rebounds#Season",
    "Assists#Season",
    "Steals#Season",
    "Blocks#Season",
    "Field Goals Made#Season",
    "Field Goals Attempted#Season",
    "Three Pointers Made#Season",
    "Three Pointers Attempted#Season",
    "Free Throws Made#Season",
    "Free Throws Attempted#Season",
    "Minutes Played#Season",
    "Offensive Rebounds#Season",
]

_AWARDS_FIELDS = [
    "Turnovers",
    "Fouls",
    "Games Started",
    "Games Played",
    "Double Doubles",
    "Triple Doubles",
    "Total +/-",
]

_SLOT_LABELS = ["0 - Current Season", "1", "2", "3", "4"]

# 24-25, 23-24, 22-23, 21-22, 20-21 from provided screenshots.
_EXPECTED_TOTALS_BY_SLOT: list[dict[str, int]] = [
    {
        "Points#Season": 1369,
        "Rebounds#Season": 174,
        "Assists#Season": 317,
        "Steals#Season": 91,
        "Blocks#Season": 21,
        "Field Goals Made#Season": 477,
        "Field Goals Attempted#Season": 1091,
        "Three Pointers Made#Season": 161,
        "Three Pointers Attempted#Season": 478,
        "Free Throws Made#Season": 254,
        "Free Throws Attempted#Season": 289,
        "Minutes Played#Season": 1960,
        "Offensive Rebounds#Season": 18,
        "Turnovers": 124,
        "Fouls": 116,
        "Games Started": 52,
        "Games Played": 52,
        "Double Doubles": 8,
        "Triple Doubles": 1,
        "Total +/-": -124,
    },
    {
        "Points#Season": 1816,
        "Rebounds#Season": 258,
        "Assists#Season": 433,
        "Steals#Season": 69,
        "Blocks#Season": 33,
        "Field Goals Made#Season": 638,
        "Field Goals Attempted#Season": 1419,
        "Three Pointers Made#Season": 212,
        "Three Pointers Attempted#Season": 569,
        "Free Throws Made#Season": 328,
        "Free Throws Attempted#Season": 378,
        "Minutes Played#Season": 2626,
        "Offensive Rebounds#Season": 35,
        "Turnovers": 116,
        "Fouls": 151,
        "Games Started": 70,
        "Games Played": 70,
        "Double Doubles": 9,
        "Triple Doubles": 0,
        "Total +/-": 303,
    },
    {
        "Points#Season": 1218,
        "Rebounds#Season": 176,
        "Assists#Season": 212,
        "Steals#Season": 49,
        "Blocks#Season": 8,
        "Field Goals Made#Season": 439,
        "Field Goals Attempted#Season": 913,
        "Three Pointers Made#Season": 160,
        "Three Pointers Attempted#Season": 369,
        "Free Throws Made#Season": 180,
        "Free Throws Attempted#Season": 213,
        "Minutes Played#Season": 2016,
        "Offensive Rebounds#Season": 21,
        "Turnovers": 80,
        "Fouls": 132,
        "Games Started": 41,
        "Games Played": 60,
        "Double Doubles": 0,
        "Triple Doubles": 0,
        "Total +/-": 241,
    },
    {
        "Points#Season": 1311,
        "Rebounds#Season": 240,
        "Assists#Season": 321,
        "Steals#Season": 55,
        "Blocks#Season": 32,
        "Field Goals Made#Season": 483,
        "Field Goals Attempted#Season": 995,
        "Three Pointers Made#Season": 132,
        "Three Pointers Attempted#Season": 309,
        "Free Throws Made#Season": 213,
        "Free Throws Attempted#Season": 246,
        "Minutes Played#Season": 2650,
        "Offensive Rebounds#Season": 22,
        "Turnovers": 88,
        "Fouls": 156,
        "Games Started": 74,
        "Games Played": 75,
        "Double Doubles": 1,
        "Triple Doubles": 0,
        "Total +/-": 192,
    },
    {
        "Points#Season": 488,
        "Rebounds#Season": 104,
        "Assists#Season": 120,
        "Steals#Season": 26,
        "Blocks#Season": 13,
        "Field Goals Made#Season": 198,
        "Field Goals Attempted#Season": 429,
        "Three Pointers Made#Season": 31,
        "Three Pointers Attempted#Season": 103,
        "Free Throws Made#Season": 61,
        "Free Throws Attempted#Season": 70,
        "Minutes Played#Season": 936,
        "Offensive Rebounds#Season": 11,
        "Turnovers": 41,
        "Fouls": 79,
        "Games Started": 8,
        "Games Played": 61,
        "Double Doubles": 0,
        "Triple Doubles": 0,
        "Total +/-": -52,
    },
]

_EXPECTED_PER_GAME_BY_SLOT: list[dict[str, float]] = [
    {"PPG": 26.3, "ORPG": 0.3, "RPG": 3.3, "APG": 6.1, "SPG": 1.7, "BPG": 0.4, "TOPG": 2.4, "FGPCT": 0.437, "TPPCT": 0.337, "FTPCT": 0.879, "MPG": 37.7},
    {"PPG": 25.9, "ORPG": 0.5, "RPG": 3.7, "APG": 6.2, "SPG": 1.0, "BPG": 0.5, "TOPG": 1.7, "FGPCT": 0.450, "TPPCT": 0.373, "FTPCT": 0.868, "MPG": 37.5},
    {"PPG": 20.3, "ORPG": 0.4, "RPG": 2.9, "APG": 3.5, "SPG": 0.8, "BPG": 0.1, "TOPG": 1.3, "FGPCT": 0.481, "TPPCT": 0.434, "FTPCT": 0.845, "MPG": 33.6},
    {"PPG": 17.5, "ORPG": 0.3, "RPG": 3.2, "APG": 4.3, "SPG": 0.7, "BPG": 0.4, "TOPG": 1.2, "FGPCT": 0.485, "TPPCT": 0.427, "FTPCT": 0.866, "MPG": 35.3},
    {"PPG": 8.0, "ORPG": 0.2, "RPG": 1.7, "APG": 2.0, "SPG": 0.4, "BPG": 0.2, "TOPG": 0.7, "FGPCT": 0.462, "TPPCT": 0.301, "FTPCT": 0.871, "MPG": 15.3},
]


def _verify_enabled() -> bool:
    raw = os.getenv("NBA2K_EDITOR_LIVE_STATS_VERIFY", "")
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _field_by_name(categories: dict[str, list[dict[str, object]]], category: str, field_name: str) -> dict[str, object]:
    fields = categories.get(category, [])
    for field in fields:
        if str(field.get("name") or "").strip() == field_name:
            return field
    raise AssertionError(f"Missing field '{category}/{field_name}' in loaded categories.")


def _season_record_ptr(base_ptr: int, stride: int, stat_id: int) -> int:
    if stat_id >= base_ptr and ((stat_id - base_ptr) % stride == 0):
        return stat_id
    return base_ptr + stat_id * stride


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _field_metadata(field: dict[str, object]) -> FieldMetadata:
    values_raw = field.get("values")
    values = tuple(str(item) for item in values_raw) if isinstance(values_raw, list) else None
    return FieldMetadata(
        offset=_to_int(field.get("offset") or field.get("address")),
        start_bit=_to_int(field.get("startBit") or field.get("start_bit") or 0),
        length=_to_int(field.get("length") or field.get("size") or 0),
        requires_deref=bool(field.get("requiresDereference") or field.get("requires_deref")),
        deref_offset=_to_int(field.get("dereferenceAddress") or field.get("deref_offset") or 0),
        values=values,
        data_type=str(field.get("type") or ""),
        byte_length=_to_int(field.get("byte_length") or field.get("byteLength") or field.get("size") or 0),
    )


def _load_live_tyrese_context() -> tuple[PlayerDataModel, Player, dict[str, list[dict[str, object]]], list[int]]:
    mem = GameMemory(MODULE_NAME)
    if not mem.open_process():
        pytest.fail("NBA2K process is not open. Start the game before running live stats verification.")

    offset_target = mem.module_name or MODULE_NAME
    initialize_offsets(target_executable=offset_target, force=True)

    model = PlayerDataModel(mem, max_players=MAX_PLAYERS)
    model.refresh_players()
    player = next((p for p in model.players if int(p.index) == 0), None)
    assert player is not None, "Could not find player index 0."
    assert str(player.first_name).strip().lower() == "tyrese"
    assert str(player.last_name).strip().lower() == "maxey"

    categories = model.categories
    pointer_key = "career_stats"
    try:
        chains, stride = model._league_pointer_meta(pointer_key)
    except Exception:
        chains, stride = [], 0
    assert stride > 0 and chains, "career_stats pointer metadata is unavailable."
    season_base_ptr = model._resolve_league_base(pointer_key, chains, None)
    assert season_base_ptr is not None and season_base_ptr > 0

    stat_ids: list[int] = []
    for id_name in _ID_FIELD_NAMES:
        meta = _field_by_name(categories, "Stats - IDs", id_name)
        raw_val = model.decode_field_value(
            entity_type="player",
            entity_index=player.index,
            category="Stats - IDs",
            field_name=id_name,
            meta=meta,
            record_ptr=player.record_ptr,
        )
        stat_ids.append(int(raw_val))

    season_ptrs = [_season_record_ptr(int(season_base_ptr), int(stride), stat_id) for stat_id in stat_ids]
    return model, player, categories, season_ptrs


@pytest.mark.skipif(sys.platform != "win32", reason="Live memory test is Windows-only.")
def test_live_tyrese_maxey_player0_stats_match_reference_table() -> None:
    if not _verify_enabled():
        pytest.skip("Set NBA2K_EDITOR_LIVE_STATS_VERIFY=1 to run live stats alignment assertions.")

    model, player, categories, season_ptrs = _load_live_tyrese_context()

    for slot_idx, season_ptr in enumerate(season_ptrs):
        expected_totals = _EXPECTED_TOTALS_BY_SLOT[slot_idx]
        actual_totals: dict[str, int] = {}

        for field_name in _SEASON_FIELDS:
            meta = _field_by_name(categories, "Stats - Season", field_name)
            value = model.decode_field_value(
                entity_type="player",
                entity_index=player.index,
                category="Stats - Season",
                field_name=field_name,
                meta=meta,
                record_ptr=season_ptr,
            )
            actual_totals[field_name] = int(value)

        for field_name in _AWARDS_FIELDS:
            meta = _field_by_name(categories, "Stats - Awards", field_name)
            value = model.decode_field_value(
                entity_type="player",
                entity_index=player.index,
                category="Stats - Awards",
                field_name=field_name,
                meta=meta,
                record_ptr=season_ptr,
            )
            actual_totals[field_name] = int(value)

        assert actual_totals == expected_totals, f"Slot {slot_idx} totals mismatch."

        gp = max(1, actual_totals["Games Played"])
        per_game_actual = {
            "PPG": actual_totals["Points#Season"] / gp,
            "ORPG": actual_totals["Offensive Rebounds#Season"] / gp,
            "RPG": actual_totals["Rebounds#Season"] / gp,
            "APG": actual_totals["Assists#Season"] / gp,
            "SPG": actual_totals["Steals#Season"] / gp,
            "BPG": actual_totals["Blocks#Season"] / gp,
            "TOPG": actual_totals["Turnovers"] / gp,
            "FGPCT": actual_totals["Field Goals Made#Season"] / max(1, actual_totals["Field Goals Attempted#Season"]),
            "TPPCT": actual_totals["Three Pointers Made#Season"] / max(1, actual_totals["Three Pointers Attempted#Season"]),
            "FTPCT": actual_totals["Free Throws Made#Season"] / max(1, actual_totals["Free Throws Attempted#Season"]),
            "MPG": actual_totals["Minutes Played#Season"] / gp,
        }
        expected_rates = _EXPECTED_PER_GAME_BY_SLOT[slot_idx]
        for key, expected in expected_rates.items():
            actual = per_game_actual[key]
            tolerance = 0.051 if key in {"PPG", "ORPG", "RPG", "APG", "SPG", "BPG", "TOPG", "MPG"} else 0.0015
            assert abs(actual - expected) <= tolerance, f"Slot {slot_idx} {key} mismatch: {actual} != {expected}"


@pytest.mark.skipif(sys.platform != "win32", reason="Live memory test is Windows-only.")
def test_live_tyrese_maxey_full_editor_season_slot_load_matches_reference_table() -> None:
    if not _verify_enabled():
        pytest.skip("Set NBA2K_EDITOR_LIVE_STATS_VERIFY=1 to run live stats alignment assertions.")

    pytest.importorskip("dearpygui.dearpygui")
    full_player_editor_mod = importlib.import_module("nba2k_editor.ui.full_player_editor")
    FullPlayerEditor = full_player_editor_mod.FullPlayerEditor

    model, player, categories, season_ptrs = _load_live_tyrese_context()
    original_dpg = full_player_editor_mod.dpg

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
    try:
        tab_name = FullPlayerEditor._SEASON_STATS_TAB
        selector_name = FullPlayerEditor._SEASON_SLOT_SELECTOR_NAME
        editor = FullPlayerEditor.__new__(FullPlayerEditor)
        editor.model = model
        editor.player = player
        editor._closed = False
        editor._loading_values = False
        editor._initializing = False
        editor._season_slot_selector_key = (tab_name, selector_name)
        editor._season_slot_defs = [
            {
                "slot": 0,
                "label": "0 - Current Season",
                "field_name": "Current Year Stat ID",
                "source_category": "Stats - IDs",
                "meta": _field_by_name(categories, "Stats - IDs", "Current Year Stat ID"),
            },
            {
                "slot": 1,
                "label": "1",
                "field_name": "STATS_ID#1",
                "source_category": "Stats - IDs",
                "meta": _field_by_name(categories, "Stats - IDs", "STATS_ID#1"),
            },
            {
                "slot": 2,
                "label": "2",
                "field_name": "STATS_ID#2",
                "source_category": "Stats - IDs",
                "meta": _field_by_name(categories, "Stats - IDs", "STATS_ID#2"),
            },
            {
                "slot": 3,
                "label": "3",
                "field_name": "STATS_ID#3",
                "source_category": "Stats - IDs",
                "meta": _field_by_name(categories, "Stats - IDs", "STATS_ID#3"),
            },
            {
                "slot": 4,
                "label": "4",
                "field_name": "STATS_ID#4",
                "source_category": "Stats - IDs",
                "meta": _field_by_name(categories, "Stats - IDs", "STATS_ID#4"),
            },
        ]
        editor._season_stat_field_keys = [(tab_name, name) for name in [*_SEASON_FIELDS, *_AWARDS_FIELDS]]

        editor.field_vars = {tab_name: {selector_name: "slot_ctrl"}}
        for idx, field_name in enumerate([*_SEASON_FIELDS, *_AWARDS_FIELDS]):
            editor.field_vars[tab_name][field_name] = f"ctrl_{idx}"

        editor.field_meta = {}
        editor.field_source_category = {}
        for field_name in _SEASON_FIELDS:
            field_def = _field_by_name(categories, "Stats - Season", field_name)
            editor.field_meta[(tab_name, field_name)] = _field_metadata(field_def)
            editor.field_source_category[(tab_name, field_name)] = "Stats - Season"
        for field_name in _AWARDS_FIELDS:
            field_def = _field_by_name(categories, "Stats - Awards", field_name)
            editor.field_meta[(tab_name, field_name)] = _field_metadata(field_def)
            editor.field_source_category[(tab_name, field_name)] = "Stats - Awards"

        captured: dict[tuple[str, str], object] = {}
        editor._apply_loaded_values = lambda values: captured.update(values)  # type: ignore[assignment]

        for slot_idx, label in enumerate(_SLOT_LABELS):
            dpg_stub.values["slot_ctrl"] = label
            resolved_ptr = editor._resolve_selected_season_record_ptr(editor.player)
            assert resolved_ptr == season_ptrs[slot_idx]
            captured.clear()
            editor._on_season_slot_changed()
            expected = {
                (tab_name, field_name): value for field_name, value in _EXPECTED_TOTALS_BY_SLOT[slot_idx].items()
            }
            assert captured == expected, f"App season-slot load mismatch for slot {slot_idx}."
    finally:
        full_player_editor_mod.dpg = original_dpg  # type: ignore[assignment]
