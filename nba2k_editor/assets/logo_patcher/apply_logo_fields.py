"""Write Logo 3, City Name, Team Name, and Historic Year fields to running NBA 2K26 process.

The game MUST be running when you call this script.

For each team ID that has a PNG in --input-dir:
  - Logo 3        <- logos/logo{id:03d}.iff
  - City Name     <- from team_mapping.json
  - Team Name     <- from team_mapping.json
  - Historic Year <- "None" (cleared)

team_mapping.json lives next to this script's parent (nba2k_editor/assets/).
City and Team Name overrides are optional -- teams absent from the JSON just
skip the name update.

Usage
-----
    python -m nba2k_editor.assets.logo_patcher.apply_logo_fields [--dry-run]
    # or still pass --input-dir explicitly to override the yaml default
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_ASSETS = _HERE.parent           # nba2k_editor/assets/
_REPO_ROOT = _ASSETS.parent.parent  # repo root
_CONFIG_PATH = _HERE / "patch_logos.yaml"
_TEAM_MAPPING = _ASSETS / "team_mapping.json"

def _load_config() -> dict:
    """Load YAML config from `patch_logos.yaml` next to this script.

    Returns an empty dict when the file is missing.
    """
    if not _CONFIG_PATH.is_file():
        return {}
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        return {}

def _load_team_mapping() -> dict[int, dict]:
    """Load team_mapping.json -> {team_id: {city_name, team_name}}."""
    if not _TEAM_MAPPING.is_file():
        return {}
    rows = json.loads(_TEAM_MAPPING.read_text(encoding="utf-8"))
    return {int(r["team_id"]): r for r in rows}


def _find_field_meta(team_categories: dict, field_name: str) -> dict | None:
    """Search Team Vitals category for the named field's offset metadata."""
    needle = field_name.strip().lower()
    for cat_name, fields in team_categories.items():
        if "team vitals" not in cat_name.lower():
            continue
        for fdef in (fields or []):
            if not isinstance(fdef, dict):
                continue
            if (fdef.get("name") or "").strip().lower() == needle:
                return fdef
    return None


def _write_field(
    model,
    team_idx: int,
    field_name: str,
    value: str,
    meta: dict,
    dry_run: bool,
) -> bool:
    if dry_run:
        print(f"           DRY RUN  {field_name} = '{value}'")
        return True
    try:
        ok = model.encode_field_value(
            entity_type="team",
            entity_index=team_idx,
            category="Team Vitals",
            field_name=field_name,
            meta=meta,
            display_value=value,
        )
        status = "OK  " if ok else "FAIL"
        print(f"           {status}  {field_name} = '{value}'")
        return bool(ok)
    except Exception as exc:
        print(f"           ERROR {field_name}: {exc}")
        return False


def apply(input_dir: Path, dry_run: bool = False) -> None:
    sys.path.insert(0, str(_REPO_ROOT))
    from nba2k_editor.core.config import MODULE_NAME
    from nba2k_editor.core.offsets import MAX_PLAYERS, initialize_offsets
    from nba2k_editor.memory.game_memory import GameMemory
    from nba2k_editor.models.data_model import PlayerDataModel

    mem = GameMemory(MODULE_NAME)
    if not mem.open_process():
        print(f"ERROR: {MODULE_NAME} is not running. Launch the game first.")
        sys.exit(1)

    try:
        initialize_offsets(target_executable=MODULE_NAME, force=True)
    except Exception as exc:
        print(f"ERROR: Failed to load offsets -- {exc}")
        sys.exit(1)

    model = PlayerDataModel(mem, max_players=MAX_PLAYERS)

    try:
        model.refresh_players()
    except Exception as exc:
        print(f"WARNING: refresh_players raised {exc!r}; continuing.")

    team_categories: dict = model.categories or {}

    # Resolve all field metas up-front
    logo3_meta         = _find_field_meta(team_categories, "Logo 3")
    city_meta          = _find_field_meta(team_categories, "City Name")
    team_name_meta     = _find_field_meta(team_categories, "Team Name")
    hist_year_meta     = _find_field_meta(team_categories, "Historic Year")

    if logo3_meta is None:
        print("ERROR: 'Logo 3' field not found in team categories.")
        sys.exit(1)
    if city_meta is None:
        print("WARNING: 'City Name' field not found -- name updates will be skipped.")
    if team_name_meta is None:
        print("WARNING: 'Team Name' field not found -- name updates will be skipped.")
    if hist_year_meta is None:
        print("WARNING: 'Historic Year' field not found -- historic year will not be cleared.")

    # team_id -> team_index (index IS the id in this game)
    team_list: list[tuple[int, str]] = getattr(model, "team_list", []) or []
    id_to_idx: dict[int, int] = {tid: tid for tid, _ in team_list}

    # Team name overrides from team_mapping.json
    team_mapping = _load_team_mapping()
    if not team_mapping:
        print("NOTE: team_mapping.json not found or empty -- only Logo 3 will be updated.")

    # Collect team IDs from PNGs in input_dir
    team_ids: list[int] = []
    for p in sorted(input_dir.glob("*.png")):
        try:
            team_ids.append(int(p.stem))
        except ValueError:
            pass

    if not team_ids:
        print(f"No team PNGs found in {input_dir}.")
        sys.exit(0)

    print(f"Updating {len(team_ids)} team(s)...\n")

    ok = 0
    fail = 0
    for team_id in team_ids:
        if team_id not in id_to_idx:
            print(f"  [{team_id:3d}]  SKIP -- team not found in game memory")
            fail += 1
            continue

        team_idx = id_to_idx[team_id]
        mapping  = team_mapping.get(team_id)
        new_logo = f"logos/logo{team_id:03d}.iff"

        city = mapping["city_name"] if mapping else None
        name = mapping["team_name"] if mapping else None

        if dry_run:
            print(f"  [{team_id:3d}]  DRY RUN")
        else:
            print(f"  [{team_id:3d}]")

        team_ok = True

        # --- Logo 3 ---
        team_ok &= _write_field(model, team_idx, "Logo 3", new_logo, logo3_meta, dry_run)

        # --- City Name ---
        if city and city_meta:
            team_ok &= _write_field(model, team_idx, "City Name", city, city_meta, dry_run)

        # --- Team Name ---
        if name and team_name_meta:
            team_ok &= _write_field(model, team_idx, "Team Name", name, team_name_meta, dry_run)

        # --- Historic Year (clear to None) ---
        if hist_year_meta:
            team_ok &= _write_field(model, team_idx, "Historic Year", "None", hist_year_meta, dry_run)

        if team_ok:
            ok += 1
        else:
            fail += 1

    print(f"\n{'-' * 50}")
    print(f"Done.  {ok}/{ok + fail} teams fully updated.")
    if fail:
        sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="apply_logo_fields",
        description="Write Logo 3, City Name, Team Name, and Historic Year fields to running NBA 2K26 process.",
    )
    parser.add_argument(
        "--input-dir", required=False,
        help="Directory of team PNGs (same as passed to patch_logos).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be written without touching memory.",
    )
    args = parser.parse_args(argv)

    config = _load_config()

    def get_opt(name, default=None):
        # CLI arg wins, else config, else default
        val = getattr(args, name, None)
        if val not in (None, False):
            return val
        return config.get(name.replace('_', '-'), config.get(name, default))

    input_dir = Path(get_opt("input_dir"))
    if not input_dir.is_dir():
        print(f"ERROR: --input-dir '{input_dir}' does not exist.")
        sys.exit(1)

    apply(input_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
