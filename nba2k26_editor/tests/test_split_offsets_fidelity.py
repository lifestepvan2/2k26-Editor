from __future__ import annotations

from nba2k_editor.core import offsets as offsets_mod


def _load_2k26_config() -> dict[str, object]:
    offsets_mod.initialize_offsets(target_executable="NBA2K26.exe", force=True)
    config = offsets_mod._offset_config
    assert isinstance(config, dict)
    return config


def _offset_entries(config: dict[str, object]) -> list[dict[str, object]]:
    raw_entries = config.get("offsets")
    assert isinstance(raw_entries, list)
    return [entry for entry in raw_entries if isinstance(entry, dict)]


def test_stats_table_categories_are_emitted_without_flat_stats_alias() -> None:
    config = _load_2k26_config()
    categories = {str(entry.get("category") or "") for entry in _offset_entries(config)}
    assert {"Stats - IDs", "Stats - Season", "Stats - Career", "Stats - Awards"} <= categories
    assert "Stats" not in categories


def test_player_stats_relations_link_ids_to_season_only() -> None:
    config = _load_2k26_config()
    relations = config.get("relations")
    assert isinstance(relations, dict)
    player_stats = relations.get("player_stats")
    assert isinstance(player_stats, dict)
    assert player_stats.get("source_category") == "Stats - IDs"
    assert player_stats.get("target_category") == "Stats - Season"
    assert player_stats.get("relation_type") == "season_only"

    id_fields = player_stats.get("id_fields")
    assert isinstance(id_fields, list)
    assert id_fields[0] == "STATSID1"
    assert "CURRENTYEARSTATID" in id_fields
    assert all(str(field).startswith("STATSID") or str(field) == "CURRENTYEARSTATID" for field in id_fields)

    season_fields = player_stats.get("target_fields")
    assert isinstance(season_fields, list)
    season_entries = [
        entry
        for entry in _offset_entries(config)
        if str(entry.get("canonical_category") or entry.get("category") or "") == "Stats - Season"
    ]
    expected_order = [
        str(entry.get("normalized_name") or entry.get("name") or "")
        for entry in sorted(
            season_entries,
            key=lambda item: (
                int(item.get("address") or 0),
                int(item.get("startBit") or item.get("start_bit") or 0),
                str(item.get("normalized_name") or item.get("name") or ""),
            ),
        )
    ]
    assert season_fields == expected_order
    assert offsets_mod.PLAYER_STATS_RELATIONS == player_stats


def test_parse_report_accounts_for_all_discovered_leaf_fields() -> None:
    config = _load_2k26_config()
    report = config.get("_parse_report")
    assert isinstance(report, dict)

    discovered = int(report.get("discovered_leaf_fields") or 0)
    emitted = int(report.get("emitted_fields") or 0)
    skipped = int(report.get("skipped_fields") or 0)
    assert discovered > 0
    assert discovered == emitted + skipped
    assert int(report.get("untracked_loss") or 0) == 0

    skipped_entries = report.get("skipped")
    assert isinstance(skipped_entries, list)
    assert len(skipped_entries) == skipped
    assert all(isinstance(entry, dict) and entry.get("reason") for entry in skipped_entries)


def test_type_normalization_covers_observed_player_types() -> None:
    config = _load_2k26_config()
    player_entries = [
        entry
        for entry in _offset_entries(config)
        if str(entry.get("source_offsets_file") or "") == "offsets_players.json"
    ]
    raw_types = {str(entry.get("type") or "") for entry in player_entries if entry.get("type")}
    assert {"Integer", "Binary", "Float", "WString", "Pointer", "binary", "String"} <= raw_types

    normalized_by_raw: dict[str, set[str]] = {}
    for entry in player_entries:
        raw_type = str(entry.get("type") or "")
        norm_type = str(entry.get("type_normalized") or "")
        if not raw_type or not norm_type:
            continue
        normalized_by_raw.setdefault(raw_type, set()).add(norm_type)

    assert normalized_by_raw.get("Integer") == {"integer"}
    assert normalized_by_raw.get("Binary") == {"binary"}
    assert normalized_by_raw.get("binary") == {"binary"}
    assert normalized_by_raw.get("Float") == {"float"}
    assert normalized_by_raw.get("WString") == {"wstring"}
    assert normalized_by_raw.get("String") == {"string"}
    assert normalized_by_raw.get("Pointer") == {"pointer"}


def test_split_entries_include_traceability_and_inference_metadata() -> None:
    config = _load_2k26_config()
    entries = _offset_entries(config)

    stats_id_entry = next(
        entry
        for entry in entries
        if str(entry.get("category") or "") == "Stats - IDs" and str(entry.get("normalized_name") or "").startswith("STATSID")
    )
    for key_name in (
        "type_normalized",
        "source_root_category",
        "source_table_group",
        "source_table_path",
        "length_inferred",
        "start_bit_inferred",
        "parse_report_entry_id",
    ):
        assert key_name in stats_id_entry
    assert stats_id_entry.get("source_root_category") == "Stats"
    assert stats_id_entry.get("source_table_group") == "Player Stat ID"

    assert any(
        entry.get("length_inferred") and str(entry.get("type_normalized") or "") == "integer"
        for entry in entries
    )
    assert any(
        entry.get("length_inferred") and str(entry.get("type_normalized") or "") == "float"
        for entry in entries
    )
    assert any(
        entry.get("length_inferred") and str(entry.get("type_normalized") or "") == "pointer"
        for entry in entries
    )


def test_version_metadata_preserves_non_core_selected_version_keys() -> None:
    config = _load_2k26_config()
    scaled_entry = next(
        entry
        for entry in _offset_entries(config)
        if isinstance(entry.get("version_metadata"), dict) and "scale" in entry["version_metadata"]
    )
    version_metadata = scaled_entry.get("version_metadata")
    assert isinstance(version_metadata, dict)
    assert version_metadata.get("scale") == 0.01
