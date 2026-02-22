"""Image processing utilities for the logo patcher.

PNG → DDS conversion via texconv.exe (Microsoft DirectXTex).
The raw BC7 pixel data (DDS minus 148-byte header) is what tld_utils needs.

DDS header sizes
----------------
Classic DDS header:  128 bytes  (DDSD_MAGIC + DDSURFACEDESC2)
DX10 extension:       20 bytes  (DDS_HEADER_DXT10, appended after classic header)

texconv always writes DX10 headers for BC7, so total header = 148 bytes.

Public API
----------
preprocess_png(png_path, width, height) -> Path
    Resize / pre-process a PNG before DDS conversion.  Pass-through for now;
    extend with autocrop / colour adjustments as needed.

convert_png_to_dds(png_path, width, height, mip_count, format_name, texconv_exe, out_dir)
    -> Path (path to generated .dds)

strip_dds_header(dds_path) -> bytes
    Read a .dds file and return the raw pixel data (header stripped).
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

# DX10 DDS header total size (128 classic + 20 DX10 extension).
_DDS_HEADER_SIZE = 148


# ---------------------------------------------------------------------------
# PNG pre-processing
# ---------------------------------------------------------------------------

def preprocess_png(png_path: str | Path, width: int, height: int) -> Path:
    """Transform *png_path* to exactly *width* × *height* before DDS conversion.

    Uses a "contain + pad" strategy:
      1. Scale the source image to fit *inside* the target rectangle while
         preserving its original aspect ratio (no stretching/squishing).
      2. Centre the scaled image on a fully-transparent RGBA canvas of the
         target size.  Any empty space becomes transparent padding.

    Returns the path to the processed PNG — may be a temp file.
    """
    src = Path(png_path)
    img = Image.open(src).convert("RGBA")

    if img.size == (width, height):
        # Already the right size — no work needed.
        return src

    # --- scale to fit (preserve aspect ratio) ---
    src_w, src_h = img.size
    scale = min(width / src_w, height / src_h)
    fit_w = int(src_w * scale)
    fit_h = int(src_h * scale)
    scaled = img.resize((fit_w, fit_h), Image.LANCZOS)

    # --- paste centred onto transparent canvas ---
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    offset_x = (width - fit_w) // 2
    offset_y = (height - fit_h) // 2
    canvas.paste(scaled, (offset_x, offset_y))

    tmp = Path(tempfile.mktemp(suffix=".png", prefix="2k26_resize_"))
    canvas.save(tmp, format="PNG")
    return tmp


# ---------------------------------------------------------------------------
# texconv wrapper
# ---------------------------------------------------------------------------

_DEFAULT_TEXCONV_PATHS: tuple[str, ...] = (
    "tools/texconv.exe",
    "texconv.exe",
)


def _find_texconv(texconv_exe: str | Path | None) -> Path:
    if texconv_exe:
        p = Path(texconv_exe)
        if p.is_file():
            return p
        raise FileNotFoundError(f"texconv not found at: {texconv_exe}")
    for candidate in _DEFAULT_TEXCONV_PATHS:
        p = Path(candidate)
        if p.is_file():
            return p
    found = shutil.which("texconv")
    if found:
        return Path(found)
    raise FileNotFoundError(
        "texconv.exe not found. Download it from "
        "https://github.com/microsoft/DirectXTex/releases "
        "and place it in the tools/ folder, or pass --texconv <path>."
    )


def convert_png_to_dds(
    png_path: str | Path,
    width: int,
    height: int,
    mip_count: int,
    format_name: str = "BC7_UNORM",
    texconv_exe: str | Path | None = None,
    out_dir: str | Path | None = None,
) -> Path:
    """Convert *png_path* to a DDS file using texconv.

    Parameters
    ----------
    png_path:    Source PNG (already resized to *width* × *height*).
    width:       Target texture width (passed for validation only).
    height:      Target texture height.
    mip_count:   Number of mip levels to generate.
    format_name: DXGI format string, e.g. "BC7_UNORM".
    texconv_exe: Path to texconv.exe; auto-detected if None.
    out_dir:     Output directory; uses a fresh temp dir if None.

    Returns the Path to the generated .dds file.
    """
    png_path = Path(png_path)
    tc = _find_texconv(texconv_exe)

    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp(prefix="2k26_dds_"))
    else:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(tc),
        "-f", format_name,
        "-m", str(mip_count),
        "-y",               # overwrite existing files
        "-o", str(out_dir),
        str(png_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"texconv failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    expected = out_dir / (png_path.stem + ".dds")
    if not expected.is_file():
        # texconv sometimes changes casing; do a case-insensitive search.
        candidates = list(out_dir.glob("*.dds"))
        if not candidates:
            raise FileNotFoundError(f"texconv ran but no .dds found in {out_dir}")
        expected = candidates[0]

    return expected


# ---------------------------------------------------------------------------
# DDS pixel data extraction
# ---------------------------------------------------------------------------

def strip_dds_header(dds_path: str | Path, header_size: int = _DDS_HEADER_SIZE) -> bytes:
    """Return the raw pixel data from *dds_path* with the header stripped.

    If the DDS file lacks the DX10 extension (e.g. an older format), pass
    ``header_size=128`` explicitly.  For BC7 output from texconv, 148 is
    always correct.
    """
    data = Path(dds_path).read_bytes()
    magic = data[:4]
    if magic != b"DDS ":
        raise ValueError(f"Not a valid DDS file (magic={magic!r}): {dds_path}")
    return data[header_size:]
