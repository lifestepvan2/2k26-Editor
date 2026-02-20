from __future__ import annotations

import pytest

pytest.importorskip("dearpygui.dearpygui")

from nba2k26_editor.models.data_model import PlayerDataModel
from nba2k26_editor.ui.full_player_editor import FullPlayerEditor


def test_prepare_stats_tabs_duplicates_awards_into_career_and_season() -> None:
    categories = {
        "Stats - Career": [{"name": "Points#Career", "offset": 1}],
        "Stats - Season": [{"name": "Points#Season", "offset": 2}],
        "Stats - Awards": [{"name": "Most Valuable Player", "offset": 3}],
        "Vitals": [{"name": "First Name", "offset": 4}],
    }

    prepared = FullPlayerEditor._prepare_stats_tabs(categories)

    assert "Career Stats" in prepared
    assert "Season Stats" in prepared
    assert "Stats - Awards" not in prepared
    assert "Stats - Career" not in prepared
    assert "Stats - Season" not in prepared
    assert "Vitals" in prepared

    career_names = [str(field.get("name")) for field in prepared["Career Stats"]]
    season_names = [str(field.get("name")) for field in prepared["Season Stats"]]
    assert "Points#Career" in career_names
    assert "Points#Season" in season_names
    assert "Most Valuable Player" in career_names
    assert "Most Valuable Player" in season_names

    career_sources = {str(field.get("name")): str(field.get("__source_category")) for field in prepared["Career Stats"]}
    season_sources = {str(field.get("name")): str(field.get("__source_category")) for field in prepared["Season Stats"]}
    assert career_sources["Points#Career"] == "Stats - Career"
    assert season_sources["Points#Season"] == "Stats - Season"
    assert career_sources["Most Valuable Player"] == "Stats - Awards"
    assert season_sources["Most Valuable Player"] == "Stats - Awards"


def test_prepare_stats_tabs_replaces_stats_ids_with_season_slot_dropdown() -> None:
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
    assert season_fields

    selector = season_fields[0]
    assert selector.get("__season_slot_selector") is True
    assert selector.get("__source_category") == "Stats - IDs"
    selector_values = selector.get("values")
    assert selector_values == ["0 - Current Season", "1", "2"]

    slot_defs = selector.get("__season_slot_defs")
    assert isinstance(slot_defs, list)
    assert [int(defn.get("slot", -1)) for defn in slot_defs] == [0, 1, 2]
    assert [str(defn.get("field_name") or "") for defn in slot_defs] == [
        "Current Year Stat ID",
        "STATS_ID#1",
        "STATS_ID#2",
    ]
    assert str(season_fields[1].get("name")) == "Points#Season"


def test_league_pointer_for_career_category_uses_career_stats_pointer() -> None:
    model = PlayerDataModel.__new__(PlayerDataModel)

    def _fake_pointer_meta(pointer_key: str):
        if pointer_key == "career_stats":
            return ([{"rva": 1}], 64)
        if pointer_key == "NBAHistory":
            return ([{"rva": 2}], 168)
        return ([], 0)

    model._league_pointer_meta = _fake_pointer_meta  # type: ignore[method-assign]

    key, chains, stride, limit = PlayerDataModel._league_pointer_for_category(model, "Career/Record Stats")
    assert key == "career_stats"
    assert chains == [{"rva": 1}]
    assert stride == 64
    assert limit == 200


def test_league_pointer_for_season_category_uses_nba_history_pointer() -> None:
    model = PlayerDataModel.__new__(PlayerDataModel)

    def _fake_pointer_meta(pointer_key: str):
        if pointer_key == "NBAHistory":
            return ([{"rva": 2}], 168)
        if pointer_key == "career_stats":
            return ([{"rva": 1}], 64)
        return ([], 0)

    model._league_pointer_meta = _fake_pointer_meta  # type: ignore[method-assign]

    key, chains, stride, limit = PlayerDataModel._league_pointer_for_category(model, "Season/Record Stats")
    assert key == "NBAHistory"
    assert chains == [{"rva": 2}]
    assert stride == 168
    assert limit == 200
