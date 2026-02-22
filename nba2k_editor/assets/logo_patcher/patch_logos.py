"""Main CLI: patch team logo IFF files from a directory of PNGs.

Usage
-----
    # With game running, generate the team→logo path map first (once):
    python -m nba2k_editor.assets.logo_patcher.generate_map

    # Then patch logos (game does NOT need to be running):
    python -m nba2k_editor.assets.logo_patcher.patch_logos \\
        --input-dir  path/to/my_logos \\
        --game-dir   "C:/Program Files (x86)/Steam/steamapps/common/NBA 2K26" \\
        [--texconv   tools/texconv.exe] \\
        [--map       nba2k_editor/assets/team_logo_map.json] \\
        [--backup] \\
        [--dry-run]

Input directory convention
---------------------------
Place one PNG per team, named by team ID: ``24.png``, ``1.png``, etc.
The file stem must be a valid integer matching a key in the logo map.

Backup
------
Pass ``--backup`` to copy the original .iff alongside the patched one
as ``<name>.iff.bak`` before overwriting.  Strongly recommended for
first-time runs.

Dry run
-------
Pass ``--dry-run`` to perform all steps except writing to disk.  The
converted DDS and rebuilt .tld are generated in temp directories but
nothing in the game install is touched.

Compression verification
------------------------
On the first run the pipeline calls diagnose_compression() on the first
IFF it processes and aborts if zlib decompression fails for any segment.
This is a one-time safety check; pass ``--skip-verify`` to skip it after
you've confirmed the expected format.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from .iff_utils import (
    cleanup_tmp, find_texture_binary_path, repack_iff,
    read_txtr, unpack_iff, write_txtr,
)
from .image_utils import convert_png_to_dds, preprocess_png, strip_dds_header
from .tld_utils import build_tld, diagnose_compression, split_dds_mips

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent
_DEFAULT_MAP = _HERE.parent / "team_logo_map.json"
_DEFAULT_TEXCONV = Path("tools") / "texconv.exe"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_map(map_path: Path) -> dict[int, str]:
    if not map_path.is_file():
        raise FileNotFoundError(
            f"Logo map not found: {map_path}\n"
            "Run `python -m nba2k_editor.assets.logo_patcher.generate_map` first."
        )
    raw = json.loads(map_path.read_text(encoding="utf-8"))
    return {int(k): str(v) for k, v in raw.items()}


def _collect_png_inputs(input_dir: Path) -> list[tuple[int, Path]]:
    """Return [(team_id, png_path), ...] for all valid *.png files in *input_dir*."""
    results: list[tuple[int, Path]] = []
    for p in sorted(input_dir.glob("*.png")):
        try:
            team_id = int(p.stem)
        except ValueError:
            print(f"  SKIP  {p.name}  — filename is not a team ID integer")
            continue
        results.append((team_id, p))
    return results


def _resolve_iff_path(game_dir: Path, logo_rel_path: str) -> Path:
    """Resolve the IFF path inside the game directory.

    *logo_rel_path* from the map is typically ``logos/logo_024.iff``.
    The game may nest it differently depending on install layout; try a
    few common locations.
    """
    candidates = [
        game_dir / logo_rel_path,
        game_dir / "mods" / logo_rel_path,
        game_dir / "Data" / logo_rel_path,
        game_dir / "Assets" / logo_rel_path,
    ]
    for c in candidates:
        if c.is_file():
            return c
    raise FileNotFoundError(
        f"IFF not found for '{logo_rel_path}' under {game_dir}.\n"
        f"Tried:\n" + "\n".join(f"  {c}" for c in candidates)
    )


# ---------------------------------------------------------------------------
# Per-team patch
# ---------------------------------------------------------------------------

def patch_one(
    team_id: int,
    png_path: Path,
    iff_path: Path,
    texconv_exe: Path | None,
    dry_run: bool,
    verify_compression: bool,
) -> bool:
    """Patch the logo IFF for one team.  Returns True on success."""
    print(f"\n  Team {team_id}  |  {png_path.name}  ->  {iff_path.name}")

    tmp_unpack: Path | None = None
    tmp_dds_dir: Path | None = None
    preprocessed: Path | None = None

    try:
        # 1. Unpack IFF
        tmp_unpack = unpack_iff(iff_path)
        txtr_meta = read_txtr(tmp_unpack)
        bin_path, bin_kind = find_texture_binary_path(tmp_unpack)

        width: int = int(txtr_meta.get("Width", 1024))
        height: int = int(txtr_meta.get("Height", 1024))
        mip_count: int = int(txtr_meta.get("Mips", 11))
        fmt: str = str(txtr_meta.get("Format", "BC7_UNORM"))

        print(f"    Texture  {width}×{height}  mips={mip_count}  fmt={fmt}  bin={bin_kind}")

        # 2. Optional: verify compression method (first call only)
        if verify_compression:
            diagnose_compression(bin_path, txtr_meta)

        # 3. Pre-process PNG (resize → RGBA)
        preprocessed_path = preprocess_png(png_path, width, height)
        if preprocessed_path != png_path:
            preprocessed = preprocessed_path  # track for cleanup

        # 4. Convert PNG → DDS
        tmp_dds_dir = Path(tempfile.mkdtemp(prefix="2k26_dds_"))
        dds_path = convert_png_to_dds(
            png_path=preprocessed_path,
            width=width,
            height=height,
            mip_count=mip_count,
            format_name=fmt,
            texconv_exe=texconv_exe,
            out_dir=tmp_dds_dir,
        )
        print(f"    DDS      {dds_path.stat().st_size} bytes  ({dds_path.name})")

        if bin_kind == "dds":
            # Direct replacement: copy converted DDS over the existing one
            if dry_run:
                print("    DRY RUN — skipping write.")
                return True
            shutil.copy2(dds_path, bin_path)
            print(f"    DONE     wrote {iff_path}  (DDS inline)")
        else:
            # TLD path: strip header → mip buffers → rebuild TLD
            # 5. Strip DDS header → raw BC7 pixel buffer, split into mip slices
            raw_pixels = strip_dds_header(dds_path)
            mip_buffers = split_dds_mips(raw_pixels, width, height, mip_count)

            # 6. Rebuild .tld
            new_tld_bytes, updated_segments = build_tld(mip_buffers, txtr_meta)
            print(f"    TLD      {len(new_tld_bytes)} bytes  ({len(updated_segments)} segments)")

            if dry_run:
                print("    DRY RUN — skipping write.")
                return True

            # 7. Write new .tld into unpacked dir
            bin_path.write_bytes(new_tld_bytes)

            # 8. Update .txtr with new segment metadata
            txtr_meta["Segments"] = updated_segments
            txtr_meta["PixelDataSize"] = len(new_tld_bytes)
            write_txtr(tmp_unpack, txtr_meta)

            print(f"    DONE     wrote {iff_path}  (TLD rebuilt)")

        # 9. Repack IFF (overwrites original)
        repack_iff(tmp_unpack, iff_path)
        return True

    except Exception as exc:
        print(f"    ERROR    {exc}")
        return False

    finally:
        if tmp_unpack:
            cleanup_tmp(tmp_unpack)
        if tmp_dds_dir:
            cleanup_tmp(tmp_dds_dir)
        if preprocessed and preprocessed.is_file():
            try:
                preprocessed.unlink()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="patch_logos",
        description="Replace NBA 2K26 team logo IFF files from a directory of PNGs.",
    )
    parser.add_argument(
        "--input-dir", required=True,
        help="Directory containing team PNGs named by team ID (e.g. 24.png).",
    )
    parser.add_argument(
        "--game-dir", required=True,
        help="Root of the NBA 2K26 game install (e.g. Steam/steamapps/common/NBA 2K26).",
    )
    parser.add_argument(
        "--texconv", default=None,
        help=f"Path to texconv.exe (default: {_DEFAULT_TEXCONV}).",
    )
    parser.add_argument(
        "--map", default=str(_DEFAULT_MAP),
        help=f"Path to team_logo_map.json (default: {_DEFAULT_MAP}).",
    )
    parser.add_argument(
        "--backup", action="store_true",
        help="Back up each original IFF as <name>.iff.bak before patching.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Perform all conversion steps but do not write any files.",
    )
    parser.add_argument(
        "--skip-verify", action="store_true",
        help="Skip the one-time zlib compression verification step.",
    )

    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir)
    game_dir = Path(args.game_dir)
    map_path = Path(args.map)
    texconv_exe = Path(args.texconv) if args.texconv else None

    if not input_dir.is_dir():
        print(f"ERROR: --input-dir '{input_dir}' does not exist or is not a directory.")
        sys.exit(1)
    if not game_dir.is_dir():
        print(f"ERROR: --game-dir '{game_dir}' does not exist or is not a directory.")
        sys.exit(1)

    # Load team → logo map
    try:
        logo_map = _load_map(map_path)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    # Collect PNGs
    png_inputs = _collect_png_inputs(input_dir)
    if not png_inputs:
        print(f"No team PNG files found in {input_dir}.")
        sys.exit(0)

    print(f"Found {len(png_inputs)} PNG(s) to process.\n")

    ok_count = 0
    fail_count = 0
    verify_next = not args.skip_verify  # run compression check on first IFF only
    donor_iff: Path | None = None  # first resolved IFF; used as template for new ones

    for team_id, png_path in png_inputs:
        logo_rel = logo_map.get(team_id)
        if logo_rel is None:
            print(f"\n  Team {team_id}  |  {png_path.name}  -- SKIP  (not in logo map)")
            fail_count += 1
            continue

        try:
            iff_path = _resolve_iff_path(game_dir, logo_rel)
        except FileNotFoundError:
            if donor_iff is None:
                print(f"\n  Team {team_id}  |  SKIP  -- IFF not found and no donor template yet.")
                fail_count += 1
                continue
            # Create a new IFF by cloning the donor structure into mods/logos/
            dest = game_dir / "mods" / logo_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(donor_iff, dest)
            iff_path = dest
            print(f"\n  Team {team_id}  |  CREATE  {Path(logo_rel).name}  (cloned from {donor_iff.name})")

        else:
            # Track the first successfully found IFF as our donor for new files
            if donor_iff is None:
                donor_iff = iff_path

        # Backup before first write
        if args.backup and not args.dry_run:
            bak = iff_path.with_suffix(".iff.bak")
            if not bak.exists():
                shutil.copy2(iff_path, bak)
                print(f"  BACKUP   {bak}")

        success = patch_one(
            team_id=team_id,
            png_path=png_path,
            iff_path=iff_path,
            texconv_exe=texconv_exe,
            dry_run=args.dry_run,
            verify_compression=verify_next,
        )
        verify_next = False  # only verify once

        if success:
            ok_count += 1
        else:
            fail_count += 1

    total = ok_count + fail_count
    print(f"\n{'-' * 50}")
    print(f"Done.  {ok_count}/{total} succeeded, {fail_count} failed.")
    if args.dry_run:
        print("(dry-run — no files were written)")

    if fail_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
