"""Main CLI: patch team logo IFF files from a directory of PNGs.

Usage
-----
    # Patch logos (game does NOT need to be running):
    python -m nba2k_editor.assets.logo_patcher.patch_logos \\
        --input-dir  path/to/my_logos \\
        --game-dir   "C:/Program Files (x86)/Steam/steamapps/common/NBA 2K26" \\
        [--texconv   tools/texconv.exe] \\
        [--backup] \\
        [--dry-run]

    # Then, with the game running, update Logo 3 pointers in-memory:
    python -m nba2k_editor.assets.logo_patcher.apply_logo_fields \\
        --input-dir  path/to/my_logos

Input directory convention
---------------------------
Place one PNG per team, named by team ID: ``38.png``, ``39.png``, etc.
The filename stem must be a plain integer team ID.

Naming convention
-----------------
Each team always gets its own IFF:  ``mods/logos/logo{team_id:03d}.iff``
If the file does not exist yet it is cloned from the bundled template and
then patched.  No two teams ever share a file.

Backup
------
Pass ``--backup`` to copy the original .iff alongside the patched one
as ``<name>.iff.bak`` before overwriting.  Strongly recommended for
first-time runs.

Dry run
-------
Pass ``--dry-run`` to perform all steps except writing to disk.  The
converted DDS is generated in a temp directory but nothing in the game
install is touched.

Compression verification
------------------------
On the first run the pipeline calls diagnose_compression() on the first
IFF it processes.  Pass ``--skip-verify`` to suppress this after the
format has been confirmed.
"""
from __future__ import annotations

import argparse
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
import yaml

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent
_DEFAULT_TEXCONV = Path("tools") / "texconv.exe"
_TEMPLATE_IFF = _HERE / "template.iff"
_CONFIG_PATH = _HERE / "patch_logos.yaml"


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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collect_png_inputs(input_dir: Path) -> list[tuple[int, Path]]:
    """Return [(team_id, png_path), ...] for all valid *.png files in *input_dir*."""
    results: list[tuple[int, Path]] = []
    for p in sorted(input_dir.glob("*.png")):
        try:
            team_id = int(p.stem)
        except ValueError:
            print(f"  SKIP  {p.name}  -- filename is not a team ID integer")
            continue
        results.append((team_id, p))
    return results


def _ensure_iff(game_dir: Path, team_id: int) -> tuple[Path, bool]:
    """Return (iff_path, is_new) for *team_id*.

    If the canonical ``mods/logos/logo{id:03d}.iff`` does not yet exist it is
    created by cloning the repo-local template so that ``patch_one`` always has
    a valid IFF to unpack.  In dry-run mode ``patch_one`` will skip the final
    write so the file is left as a pristine template clone.
    """
    iff_path = game_dir / "mods" / "logos" / f"logo{team_id:03d}.iff"
    if iff_path.is_file():
        return iff_path, False
    if not _TEMPLATE_IFF.is_file():
        raise FileNotFoundError(
            f"Template IFF not found at {_TEMPLATE_IFF}. "
            "Re-run setup or restore the file."
        )
    iff_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(_TEMPLATE_IFF, iff_path)
    return iff_path, True


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
        description=(
            "Build/replace NBA 2K26 team logo IFFs from PNGs. "
            "Each team always gets logos/logo{id:03d}.iff -- no shared files."
        ),
    )
    parser.add_argument(
        "--input-dir", required=False,
        help="Directory containing team PNGs named by team ID (e.g. 38.png).",
    )
    parser.add_argument(
        "--game-dir", required=False,
        help="Root of the NBA 2K26 game install.",
    )
    parser.add_argument(
        "--texconv", default=None,
        help=f"Path to texconv.exe (default: auto-detect from {_DEFAULT_TEXCONV}).",
    )
    parser.add_argument(
        "--backup", action="store_true",
        help="Back up each IFF as <name>.iff.bak before overwriting.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Convert but do not write any files to disk.",
    )
    parser.add_argument(
        "--skip-verify", action="store_true",
        help="Skip the one-time compression verification step.",
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
    game_dir = Path(get_opt("game_dir"))
    texconv_exe = Path(get_opt("texconv")) if get_opt("texconv") else None
    backup = bool(get_opt("backup", False))
    dry_run = bool(get_opt("dry_run", False))
    skip_verify = bool(get_opt("skip_verify", False))

    if not input_dir.is_dir():
        print(f"ERROR: --input-dir '{input_dir}' does not exist or is not a directory.")
        sys.exit(1)
    if not game_dir.is_dir():
        print(f"ERROR: --game-dir '{game_dir}' does not exist or is not a directory.")
        sys.exit(1)

    # Collect PNGs
    png_inputs = _collect_png_inputs(input_dir)
    if not png_inputs:
        print(f"No team PNG files found in {input_dir}.")
        sys.exit(0)

    print(f"Found {len(png_inputs)} PNG(s) to process.\n")

    ok_count = 0
    fail_count = 0
    verify_next = not skip_verify

    for team_id, png_path in png_inputs:
        logo_filename = f"logo{team_id:03d}.iff"
        print(f"\n  Team {team_id}  |  {png_path.name}  ->  {logo_filename}")

        try:
            iff_path, is_new = _ensure_iff(game_dir, team_id)
            if is_new:
                print(f"  CREATE   {iff_path.name}  (from template)")
        except Exception as exc:
            print(f"    ERROR    {exc}")
            fail_count += 1
            continue

        # Backup before first write
        if backup and not dry_run and iff_path.exists():
            bak = iff_path.with_suffix(".iff.bak")
            if not bak.exists():
                shutil.copy2(iff_path, bak)
                print(f"  BACKUP   {bak}")

        success = patch_one(
            team_id=team_id,
            png_path=png_path,
            iff_path=iff_path,
            texconv_exe=texconv_exe,
            dry_run=dry_run,
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
    if dry_run:
        print("(dry-run -- no files were written)")
    else:
        print("Run apply_logo_fields.py (game running) to update Logo 3 pointers.")

    if fail_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
