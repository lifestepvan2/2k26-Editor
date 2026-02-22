from __future__ import annotations

from copy import deepcopy

import pytest

from nba2k_editor.core import offsets as offsets_mod
from nba2k_editor.models.data_model import PlayerDataModel


_OFFSET_STATE_KEYS = (
    "MODULE_NAME",
    "PLAYER_TABLE_RVA",
    "PLAYER_STRIDE",
    "PLAYER_PTR_CHAINS",
    "DRAFT_PTR_CHAINS",
    "OFF_LAST_NAME",
    "OFF_FIRST_NAME",
    "OFF_TEAM_PTR",
    "OFF_TEAM_ID",
    "OFF_TEAM_NAME",
    "NAME_MAX_CHARS",
    "FIRST_NAME_ENCODING",
    "LAST_NAME_ENCODING",
    "TEAM_NAME_ENCODING",
    "TEAM_STRIDE",
    "TEAM_NAME_OFFSET",
    "TEAM_NAME_LENGTH",
    "TEAM_PLAYER_SLOT_COUNT",
    "TEAM_PTR_CHAINS",
    "TEAM_TABLE_RVA",
    "TEAM_FIELD_DEFS",
    "TEAM_RECORD_SIZE",
    "STAFF_STRIDE",
    "STAFF_RECORD_SIZE",
    "STAFF_PTR_CHAINS",
    "STAFF_NAME_OFFSET",
    "STAFF_NAME_LENGTH",
    "STAFF_NAME_ENCODING",
    "STADIUM_STRIDE",
    "STADIUM_RECORD_SIZE",
    "STADIUM_PTR_CHAINS",
    "STADIUM_NAME_OFFSET",
    "STADIUM_NAME_LENGTH",
    "STADIUM_NAME_ENCODING",
    "_offset_index",
    "_offset_normalized_index",
)


@pytest.fixture()
def restore_offsets_state():
    snapshot = {key: deepcopy(getattr(offsets_mod, key)) for key in _OFFSET_STATE_KEYS}
    yield
    for key, value in snapshot.items():
        setattr(offsets_mod, key, value)


def _entry(
    *,
    category: str,
    name: str,
    canonical_category: str,
    normalized_name: str,
    address: int,
    length: int,
    type_name: str = "WString",
    dereference_address: int | None = None,
) -> dict[str, object]:
    entry: dict[str, object] = {
        "category": category,
        "name": name,
        "canonical_category": canonical_category,
        "normalized_name": normalized_name,
        "address": address,
        "length": length,
        "type": type_name,
    }
    if dereference_address is not None:
        entry["dereferenceAddress"] = dereference_address
    return entry


def _strict_offsets_payload() -> dict[str, object]:
    return {
        "offsets": [
            _entry(
                category="Vitals",
                name="First Name",
                canonical_category="Vitals",
                normalized_name="FIRSTNAME",
                address=0x10,
                length=20,
            ),
            _entry(
                category="Vitals",
                name="Last Name",
                canonical_category="Vitals",
                normalized_name="LASTNAME",
                address=0x30,
                length=20,
            ),
            _entry(
                category="Vitals",
                name="Current Team",
                canonical_category="Vitals",
                normalized_name="CURRENTTEAM",
                address=0x58,
                length=4,
                type_name="Integer",
                dereference_address=0x8,
            ),
            _entry(
                category="Team Vitals",
                name="Team Name",
                canonical_category="Team Vitals",
                normalized_name="TEAMNAME",
                address=0x100,
                length=24,
            ),
            _entry(
                category="Team Vitals",
                name="City Name",
                canonical_category="Team Vitals",
                normalized_name="CITYNAME",
                address=0x140,
                length=24,
            ),
            _entry(
                category="Team Vitals",
                name="City Abbrev",
                canonical_category="Team Vitals",
                normalized_name="CITYABBREV",
                address=0x170,
                length=4,
                type_name="String",
            ),
            _entry(
                category="Staff Vitals",
                name="First Name",
                canonical_category="Staff Vitals",
                normalized_name="FIRSTNAME",
                address=0x20,
                length=20,
            ),
            _entry(
                category="Staff Vitals",
                name="Last Name",
                canonical_category="Staff Vitals",
                normalized_name="LASTNAME",
                address=0x48,
                length=20,
            ),
            _entry(
                category="Stadium",
                name="Arena Name",
                canonical_category="Stadium",
                normalized_name="ARENANAME",
                address=0x90,
                length=32,
            ),
            _entry(
                category="Team Players",
                name="Slot 0",
                canonical_category="Team Players",
                normalized_name="PLAYER0",
                address=0x0,
                length=8,
                type_name="Integer",
            ),
        ],
        "base_pointers": {
            "Player": {"address": 130990776, "chain": []},
            "Team": {"address": 130991376, "chain": []},
            "Staff": {"address": 130991496, "chain": []},
            "Stadium": {"address": 130992024, "chain": []},
            "Cursor": {"address": 0, "chain": []},
            "TeamHistory": {"address": 130991376, "chain": []},
            "NBAHistory": {"address": 130991424, "chain": []},
            "HallOfFame": {"address": 130991424, "chain": []},
            "History": {"address": 130991424, "chain": []},
            "Jersey": {"address": 130991400, "chain": []},
            "career_stats": {"address": 130990680, "chain": []},
        },
        "game_info": {
            "playerSize": 1176,
            "teamSize": 5672,
            "staffSize": 1000,
            "stadiumSize": 1024,
            "historySize": 256,
            "hall_of_fameSize": 300,
            "career_statsSize": 400,
            "jerseySize": 64,
        },
    }


def _new_league_model_stub() -> PlayerDataModel:
    model = PlayerDataModel.__new__(PlayerDataModel)
    model._league_pointer_cache = {}
    return model


def test_apply_offset_config_accepts_exact_mapping_for_all_base_pointer_keys(restore_offsets_state) -> None:
    payload = _strict_offsets_payload()

    offsets_mod._apply_offset_config(payload)

    assert offsets_mod.PLAYER_STRIDE == 1176
    assert offsets_mod.TEAM_STRIDE == 5672
    assert offsets_mod.STAFF_STRIDE == 1000
    assert offsets_mod.STADIUM_STRIDE == 1024
    assert offsets_mod.OFF_FIRST_NAME == 0x10
    assert offsets_mod.OFF_LAST_NAME == 0x30
    assert offsets_mod.TEAM_NAME_OFFSET == 0x100
    assert offsets_mod.STADIUM_NAME_OFFSET == 0x90


def test_apply_offset_config_rejects_case_variant_base_pointer_key(restore_offsets_state) -> None:
    payload = _strict_offsets_payload()
    base_pointers = payload["base_pointers"]
    assert isinstance(base_pointers, dict)
    base_pointers["player"] = base_pointers.pop("Player")

    with pytest.raises(offsets_mod.OffsetSchemaError, match="Missing required base pointer 'Player'"):
        offsets_mod._apply_offset_config(payload)


def test_apply_offset_config_rejects_case_variant_size_key(restore_offsets_state) -> None:
    # Required-pointer size keys must match exactly (case-sensitive).
    payload = _strict_offsets_payload()
    game_info = payload["game_info"]
    assert isinstance(game_info, dict)
    game_info["TeamSize"] = game_info.pop("teamSize")

    with pytest.raises(offsets_mod.OffsetSchemaError, match="teamSize"):
        offsets_mod._apply_offset_config(payload)


def test_apply_offset_config_fails_when_required_size_missing(restore_offsets_state) -> None:
    # Deleting a required pointer's size key must raise an error.
    payload = _strict_offsets_payload()
    game_info = payload["game_info"]
    assert isinstance(game_info, dict)
    del game_info["playerSize"]

    with pytest.raises(offsets_mod.OffsetSchemaError, match="playerSize"):
        offsets_mod._apply_offset_config(payload)


def test_apply_offset_config_does_not_fallback_to_team_stadium_for_stadium_name(restore_offsets_state) -> None:
    payload = _strict_offsets_payload()
    offsets_list = payload["offsets"]
    assert isinstance(offsets_list, list)
    for entry in offsets_list:
        if (
            isinstance(entry, dict)
            and entry.get("canonical_category") == "Stadium"
            and entry.get("normalized_name") == "ARENANAME"
        ):
            entry["canonical_category"] = "Team Stadium"
            entry["category"] = "Team Stadium"

    with pytest.raises(offsets_mod.OffsetSchemaError, match="Stadium/ARENANAME"):
        offsets_mod._apply_offset_config(payload)


def test_league_pointer_meta_ignores_case_variant_pointer_keys() -> None:
    model = _new_league_model_stub()
    model._league_context = lambda: (  # type: ignore[method-assign]
        {"nbahistory": {"address": 123456, "chain": []}},
        {"historySize": 96},
    )

    chains, stride = PlayerDataModel._league_pointer_meta(model, "NBAHistory")

    assert chains == []
    assert stride == 96


def test_league_stride_requires_exact_mapped_size_key() -> None:
    model = _new_league_model_stub()

    assert PlayerDataModel._league_stride(model, "History", {"historySize": 96}) == 96
    assert PlayerDataModel._league_stride(model, "NBAHistory", {"HistorySize": 96}) == 0


def test_resolve_version_context_prefers_top_level_base_pointers_and_version_game_info() -> None:
    payload: dict[str, object] = {
        "base_pointers": {"Player": {"address": 111}},
        "game_info": {"playerSize": 1176},
        "versions": {
            "2K26": {
                "base_pointers": {"Player": {"address": 222}},
                "game_info": {"playerSize": 2048},
            }
        },
    }

    version_label, base_pointers, game_info = offsets_mod._resolve_version_context(payload, "NBA2K26.exe")

    assert version_label == "2K26"
    assert isinstance(base_pointers.get("Player"), dict)
    assert base_pointers["Player"]["address"] == 111
    assert game_info["playerSize"] == 2048


def test_resolve_version_context_falls_back_to_version_base_pointers_when_top_level_missing() -> None:
    payload: dict[str, object] = {
        "game_info": {"playerSize": 1176},
        "versions": {
            "2K26": {
                "base_pointers": {"Team": {"address": 333}},
                "game_info": {"playerSize": 2048},
            }
        },
    }

    version_label, base_pointers, game_info = offsets_mod._resolve_version_context(payload, "NBA2K26.exe")

    assert version_label == "2K26"
    assert isinstance(base_pointers.get("Team"), dict)
    assert base_pointers["Team"]["address"] == 333
    assert game_info["playerSize"] == 2048


def test_league_context_delegates_to_offsets_resolver(monkeypatch) -> None:
    model = _new_league_model_stub()
    model.mem = type("MemStub", (), {"module_name": "NBA2K26.exe"})()
    cfg = {"versions": {}}
    expected_base = {"NBAHistory": {"address": 123456}}
    expected_game = {"historySize": 96}
    calls: list[tuple[object, object]] = []

    def _fake_resolve(data, target):
        calls.append((data, target))
        return "2K26", expected_base, expected_game

    monkeypatch.setattr(offsets_mod, "_offset_config", cfg, raising=False)
    monkeypatch.setattr(offsets_mod, "_current_offset_target", "nba2k26.exe", raising=False)
    monkeypatch.setattr(offsets_mod, "_resolve_version_context", _fake_resolve, raising=True)

    base_pointers, game_info = PlayerDataModel._league_context(model)

    assert calls == [(cfg, "nba2k26.exe")]
    assert base_pointers == expected_base
    assert game_info == expected_game


def test_league_pointer_meta_does_not_build_fallback_chain_when_parser_returns_empty(monkeypatch) -> None:
    model = _new_league_model_stub()
    model._league_context = lambda: (  # type: ignore[method-assign]
        {"NBAHistory": {"address": 123456, "chain": [{"offset": 8}]}},
        {"historySize": 96},
    )
    monkeypatch.setattr(offsets_mod, "_parse_pointer_chain_config", lambda _def: [], raising=True)

    chains, stride = PlayerDataModel._league_pointer_meta(model, "NBAHistory")

    assert chains == []
    assert stride == 96


def test_league_pointer_meta_uses_canonical_parser_output(monkeypatch) -> None:
    model = _new_league_model_stub()
    canonical_chains = [
        {
            "rva": 987654,
            "steps": [{"offset": 16, "post_add": 0, "dereference": True}],
            "final_offset": 24,
            "absolute": False,
            "direct_table": False,
        }
    ]
    model._league_context = lambda: (  # type: ignore[method-assign]
        {"NBAHistory": {"address": 123456, "chain": [{"offset": 8}]}},
        {"historySize": 96},
    )
    monkeypatch.setattr(offsets_mod, "_parse_pointer_chain_config", lambda _def: canonical_chains, raising=True)

    chains, stride = PlayerDataModel._league_pointer_meta(model, "NBAHistory")

    assert chains == canonical_chains
    assert stride == 96
