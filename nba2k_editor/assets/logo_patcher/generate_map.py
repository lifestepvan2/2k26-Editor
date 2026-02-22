"""One-time generator: scan live game memory and build team_logo_map.json.

Usage (game must be running):
    python -m nba2k_editor.assets.logo_patcher.generate_map

Writes:
    nba2k_editor/assets/team_logo_map.json

The output is a single source-of-truth mapping:
    { "<team_id>": "logos/logo_024.iff", ... }

This file is committed to the repo and consumed by patch_logos.py.
It only needs to be regenerated when the game receives a patch that
changes team logo paths.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Resolve repo root (3 levels up from this file: logo_patcher/ → assets/ → nba2k_editor/ → root)
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_OUT_PATH = Path(__file__).resolve().parent.parent / "team_logo_map.json"

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def generate(out_path: Path = _OUT_PATH) -> None:
    # Import inside function so the module can be imported without side-effects.
    sys.path.insert(0, str(_REPO_ROOT))
    from nba2k_editor.core.config import MODULE_NAME
    from nba2k_editor.core.offsets import MAX_PLAYERS, initialize_offsets
    from nba2k_editor.memory.game_memory import GameMemory
    from nba2k_editor.models.data_model import PlayerDataModel

    mem = GameMemory(MODULE_NAME)
    if not mem.open_process():
        print(f"ERROR: {MODULE_NAME} is not running. Launch the game and try again.")
        sys.exit(1)

    try:
        initialize_offsets(target_executable=MODULE_NAME, force=True)
    except Exception as exc:
        print(f"ERROR: Failed to load offsets — {exc}")
        sys.exit(1)

    model = PlayerDataModel(mem, max_players=MAX_PLAYERS)

    print("Scanning team list …")
    try:
        model.refresh_players()
    except Exception as exc:
        print(f"WARNING: refresh_players raised {exc!r}; continuing with team list only.")

    team_list: list[tuple[int, str]] = getattr(model, "team_list", []) or []
    if not team_list:
        print("ERROR: No teams found. Make sure the game is running and offsets are loaded correctly.")
        sys.exit(1)

    # Find the Logo 3 field metadata from the loaded categories.
    team_categories: dict = model.categories or {}
    logo3_meta: dict | None = None
    for cat_name, fields in team_categories.items():
        if "team vitals" not in cat_name.lower():
            continue
        for fdef in (fields or []):
            if not isinstance(fdef, dict):
                continue
            if (fdef.get("name") or "").strip().lower() == "logo 3":
                logo3_meta = fdef
                break
        if logo3_meta:
            break

    if logo3_meta is None:
        print("ERROR: 'Logo 3' field not found in team categories. Are the offsets loaded correctly?")
        sys.exit(1)

    print(f"Found {len(team_list)} teams. Reading Logo 3 paths …\n")

    logo_map: dict[str, str] = {}
    failed: list[int] = []

    for team_idx, team_name in sorted(team_list):
        try:
            logo_path_raw = model.decode_field_value(
                entity_type="team",
                entity_index=team_idx,
                category="Team Vitals",
                field_name="Logo 3",
                meta=logo3_meta,
            )
        except Exception:
            logo_path_raw = None

        if not logo_path_raw:
            print(f"  [{team_idx:3d}] {team_name:<30s}  — Logo 3 EMPTY / unreadable")
            failed.append(team_idx)
            continue

        logo_path = str(logo_path_raw).strip().rstrip("\x00")
        logo_map[str(team_idx)] = logo_path
        print(f"  [{team_idx:3d}] {team_name:<30s}  → {logo_path}")

    if failed:
        print(f"\nWARNING: {len(failed)} teams had no Logo 3 value: {failed}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(logo_map, indent=2, sort_keys=True), encoding="utf-8")
    print(f"\nWrote {len(logo_map)} entries to {out_path}")


if __name__ == "__main__":
    generate()
