"""IFF archive unpack / repack utilities.

NBA 2K stores many assets (logos, courts, jerseys …) as ZIP-compatible IFF
files.  Each IFF contains a JSON metadata file (<name>.txtr) and one or more
binary segment files (<name>.<hash>.tld).

Public API
----------
unpack_iff(iff_path) -> pathlib.Path          extract to a temp dir
read_txtr(unpacked_dir)  -> dict              parse the .txtr JSON
write_txtr(unpacked_dir, meta)               overwrite the .txtr JSON
repack_iff(unpacked_dir, dest_path)          zip dir back to a single .iff
"""
from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Unpack
# ---------------------------------------------------------------------------

def unpack_iff(iff_path: str | Path) -> Path:
    """Extract *iff_path* into a fresh temporary directory and return its Path.

    The caller is responsible for cleaning up the directory when done
    (use :func:`cleanup_tmp` or a ``try/finally`` block).
    """
    iff_path = Path(iff_path)
    if not iff_path.is_file():
        raise FileNotFoundError(f"IFF not found: {iff_path}")

    tmp = Path(tempfile.mkdtemp(prefix="2k26_iff_"))
    try:
        with zipfile.ZipFile(iff_path, "r") as zf:
            zf.extractall(tmp)
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return tmp


def cleanup_tmp(tmp_dir: str | Path) -> None:
    """Remove a temporary directory created by :func:`unpack_iff`."""
    shutil.rmtree(str(tmp_dir), ignore_errors=True)


# ---------------------------------------------------------------------------
# .txtr metadata
# ---------------------------------------------------------------------------

def _find_txtr(unpacked_dir: Path) -> Path:
    matches = list(unpacked_dir.glob("*.txtr"))
    if not matches:
        raise FileNotFoundError(f"No .txtr file found in {unpacked_dir}")
    if len(matches) > 1:
        raise ValueError(f"Multiple .txtr files found in {unpacked_dir}: {matches}")
    return matches[0]


def read_txtr(unpacked_dir: str | Path) -> dict:
    """Parse and return the .txtr JSON metadata from *unpacked_dir*."""
    unpacked_dir = Path(unpacked_dir)
    txtr_path = _find_txtr(unpacked_dir)
    raw = txtr_path.read_text(encoding="utf-8-sig").strip()
    # .txtr files are stored as a bare key:value pair without wrapping braces,
    # e.g.  "logo": { "Width": 1024, ... }
    # Wrap in {} to make it valid JSON before parsing.
    if not raw.startswith("{"):
        raw = "{" + raw + "}"
    data = json.loads(raw)
    # Unwrap the single top-level key so callers receive the inner dict directly.
    if len(data) == 1:
        return next(iter(data.values()))
    return data


def write_txtr(unpacked_dir: str | Path, meta: dict) -> None:
    """Overwrite the .txtr file in *unpacked_dir* with *meta*.

    The wrapper key (texture name) and the bare key:value format are preserved
    from the original file.
    """
    unpacked_dir = Path(unpacked_dir)
    txtr_path = _find_txtr(unpacked_dir)
    original_raw = txtr_path.read_text(encoding="utf-8-sig").strip()
    if not original_raw.startswith("{"):
        wrapped = "{" + original_raw + "}"
    else:
        wrapped = original_raw
    original_data = json.loads(wrapped)

    if len(original_data) == 1:
        wrapper_key = next(iter(original_data))
        inner_json = json.dumps(meta, indent="\t")
        # Write as bare  "key": { ... }  — no outer braces — to match the
        # original .txtr format that the game expects.
        out_text = f'"{wrapper_key}": {inner_json}'
    else:
        out_text = json.dumps(meta, indent="\t")

    txtr_path.write_text(out_text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Find .tld binary
# ---------------------------------------------------------------------------

def find_tld_path(unpacked_dir: str | Path) -> Path:
    """Return the path to the single .tld binary segment file."""
    unpacked_dir = Path(unpacked_dir)
    matches = list(unpacked_dir.glob("*.tld"))
    if not matches:
        raise FileNotFoundError(f"No .tld file found in {unpacked_dir}")
    if len(matches) > 1:
        raise ValueError(f"Multiple .tld files in {unpacked_dir}: {matches}")
    return matches[0]


def find_dds_path(unpacked_dir: str | Path) -> Path:
    """Return the path to the single .dds texture file."""
    unpacked_dir = Path(unpacked_dir)
    matches = list(unpacked_dir.glob("*.dds"))
    if not matches:
        raise FileNotFoundError(f"No .dds file found in {unpacked_dir}")
    if len(matches) > 1:
        raise ValueError(f"Multiple .dds files in {unpacked_dir}: {matches}")
    return matches[0]


def find_texture_binary_path(unpacked_dir: str | Path) -> tuple[Path, str]:
    """Find the texture binary inside an unpacked IFF, regardless of format.

    Returns (path, kind) where kind is ``'dds'`` or ``'tld'``.
    Prefers .dds when both exist (mod-friendly exports use .dds directly).
    """
    unpacked_dir = Path(unpacked_dir)
    dds = list(unpacked_dir.glob("*.dds"))
    tld = list(unpacked_dir.glob("*.tld"))
    if dds:
        return dds[0], "dds"
    if tld:
        return tld[0], "tld"
    raise FileNotFoundError(
        f"No .dds or .tld texture binary found in {unpacked_dir}\n"
        f"Contents: {[p.name for p in unpacked_dir.iterdir()]}"
    )


# ---------------------------------------------------------------------------
# Repack (zip → .iff)
# ---------------------------------------------------------------------------

def repack_iff(unpacked_dir: str | Path, dest_path: str | Path) -> None:
    """Zip all files in *unpacked_dir* and write the archive to *dest_path*.

    The original IFF is overwritten.  The archive uses ZIP_STORED (no extra
    compression) because the texture segments handle their own compression.
    """
    unpacked_dir = Path(unpacked_dir)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temp file first, then atomically replace dest.
    tmp_out = dest_path.with_suffix(".iff.tmp")
    try:
        with zipfile.ZipFile(tmp_out, "w", compression=zipfile.ZIP_STORED) as zf:
            for file in sorted(unpacked_dir.iterdir()):
                if file.is_file():
                    zf.write(file, arcname=file.name)
        tmp_out.replace(dest_path)
    except Exception:
        tmp_out.unlink(missing_ok=True)
        raise
