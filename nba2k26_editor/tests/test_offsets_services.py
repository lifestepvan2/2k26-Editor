from __future__ import annotations

import json
from pathlib import Path

from nba2k_editor.core import offsets as offsets_mod
from nba2k_editor.core.offset_cache import CachedOffsetPayload, OffsetCache
from nba2k_editor.core.offset_loader import OffsetRepository
from nba2k_editor.core.offset_resolver import OffsetResolveError, OffsetResolver


def test_offset_cache_target_roundtrip():
    cache = OffsetCache()
    payload = CachedOffsetPayload(path=Path("Offsets/offsets_league.json"), target_key="nba2k26.exe", data={"offsets": []})
    cache.set_target(payload)
    fetched = cache.get_target("nba2k26.exe")
    assert fetched is not None
    assert fetched.path == payload.path
    cache.invalidate_target("nba2k26.exe")
    assert cache.get_target("nba2k26.exe") is None


def test_offset_resolver_prefers_converted_payload():
    resolver = OffsetResolver(
        convert_schema=lambda raw, _target: {"offsets": []} if isinstance(raw, dict) and raw.get("merged") else None,
        select_entry=lambda raw, _target: raw if isinstance(raw, dict) else None,
    )
    assert resolver.resolve({"merged": True}, "nba2k26.exe") == {"offsets": []}
    assert resolver.resolve({"a": 1}, "nba2k26.exe") == {"a": 1}


def test_offset_resolver_require_dict_raises():
    resolver = OffsetResolver(
        convert_schema=lambda raw, _target: None,
        select_entry=lambda raw, _target: None,
    )
    try:
        resolver.require_dict(["bad"], "nba2k26.exe")
    except OffsetResolveError:
        pass
    else:
        raise AssertionError("OffsetResolveError was not raised.")


def test_offset_repository_loads_and_caches(tmp_path: Path):
    offsets_dir = tmp_path / "Offsets"
    offsets_dir.mkdir(parents=True, exist_ok=True)
    payload = {"offsets": [{"category": "Vitals", "name": "First Name", "address": 1, "length": 2}]}
    (offsets_dir / "offsets_league.json").write_text(json.dumps(payload), encoding="utf-8")
    repo = OffsetRepository()
    resolver = OffsetResolver(
        convert_schema=lambda raw, _target: raw if isinstance(raw, dict) else None,
        select_entry=lambda raw, _target: raw if isinstance(raw, dict) else None,
    )
    path, data = repo.load_offsets(
        target_executable="nba2k26.exe",
        search_dirs=[offsets_dir],
        candidates=["offsets_league.json"],
        resolver=resolver,
    )
    assert path is not None
    assert data is not None
    assert data["offsets"][0]["name"] == "First Name"
    # second call should return from cache
    path2, data2 = repo.load_offsets(
        target_executable="nba2k26.exe",
        search_dirs=[offsets_dir],
        candidates=["offsets_league.json"],
        resolver=resolver,
    )
    assert path2 == path
    assert data2 == data


def test_initialize_offsets_applies_explicit_filename_even_when_target_cached(tmp_path: Path, monkeypatch):
    custom_path = tmp_path / "custom_offsets.json"
    custom_payload = {"offsets": []}
    custom_path.write_text(json.dumps(custom_payload), encoding="utf-8")

    monkeypatch.setattr(offsets_mod, "_offset_config", {"offsets": [{"name": "Old"}]})
    monkeypatch.setattr(offsets_mod, "_current_offset_target", "nba2k26.exe")
    monkeypatch.setattr(offsets_mod, "MODULE_NAME", "nba2k26.exe")
    monkeypatch.setattr(offsets_mod, "_sync_player_stats_relations", lambda _data: None)

    applied_payloads: list[dict] = []

    def _fake_apply_offset_config(data: dict | None) -> None:
        if isinstance(data, dict):
            applied_payloads.append(dict(data))

    monkeypatch.setattr(offsets_mod, "_apply_offset_config", _fake_apply_offset_config)

    offsets_mod.initialize_offsets(
        target_executable="nba2k26.exe",
        force=False,
        filename=str(custom_path),
    )

    assert applied_payloads
    assert applied_payloads[-1] == custom_payload
