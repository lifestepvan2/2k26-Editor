"""Build and replace .tld segment binaries for NBA 2K texture IFFs.

Background
----------
A .tld file stores all mip levels of a texture as a sequence of segments.
The .txtr JSON describes each segment:

    {
        "FileOffset":   <int>,   # byte offset in the .tld
        "FileSize":     <int>,   # on-disk size of this segment
        "MemoryOffset": <int>,   # expected position when loaded into VRAM
        "MemorySize":   <int>,   # expected size in VRAM (must be BC7-block-aligned)
        "InflatedSize": <int>,   # ONLY present when the segment is zlib-compressed
        "MinMip":       <int>,
        "MaxMip":       <int>,
    }

Segments WITHOUT "InflatedSize" are stored raw.
Segments WITH    "InflatedSize" are zlib-compressed (CompressionMethod 33).

The segment list covers mip levels from smallest (high mip number) to
largest (mip 0), matching the on-disk order.

The last segment (highest-res / mip 0) may omit MinMip/MaxMip in the original
data — treat it as mip 0 only.

Public API
----------
build_tld(raw_bc7_mips, txtr_meta) -> (tld_bytes, updated_segments)
    Rebuilds the .tld binary from a list of raw BC7 mip buffers and returns
    the new bytes together with updated segment metadata.

diagnose_compression(tld_path, txtr_meta) -> None
    Prints whether zlib decompression of each compressed segment succeeds,
    helping verify that CompressionMethod 33 == zlib before full patching.
"""
from __future__ import annotations

import math
import zlib
from pathlib import Path
from typing import NamedTuple


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def bc7_mip_size(width: int, height: int, mip: int) -> int:
    """Return the raw byte size of one BC7 mip level.

    BC7 encodes in 4×4 blocks, 16 bytes each.
    """
    w = max(1, width >> mip)
    h = max(1, height >> mip)
    blocks_w = math.ceil(w / 4)
    blocks_h = math.ceil(h / 4)
    return blocks_w * blocks_h * 16


def split_dds_mips(dds_bytes: bytes, width: int, height: int, mip_count: int) -> list[bytes]:
    """Split a flat DDS pixel buffer (header already stripped) into per-mip chunks.

    Returns a list of *mip_count* byte strings ordered mip-0 first (largest).
    """
    mips: list[bytes] = []
    offset = 0
    for mip in range(mip_count):
        size = bc7_mip_size(width, height, mip)
        mips.append(dds_bytes[offset : offset + size])
        offset += size
    return mips


# ---------------------------------------------------------------------------
# Segment building
# ---------------------------------------------------------------------------

class SegmentMeta(NamedTuple):
    file_offset: int
    file_size: int
    memory_offset: int
    memory_size: int
    min_mip: int
    max_mip: int
    inflated_size: int | None  # None → raw stored


def _is_compressed(seg: dict) -> bool:
    return "InflatedSize" in seg


def _build_segment(seg_def: dict, mip_data: bytes) -> tuple[bytes, dict]:
    """Produce the on-disk bytes for one segment and the updated metadata dict.

    *seg_def* is the original segment dict from the .txtr.
    *mip_data* is the concatenated raw BC7 bytes for the mips this segment covers.
    """
    if _is_compressed(seg_def):
        stored = zlib.compress(mip_data, level=9)
        inflated_size = len(mip_data)
    else:
        stored = mip_data
        inflated_size = None

    updated: dict = dict(seg_def)
    updated["FileSize"] = len(stored)
    updated["MemorySize"] = len(mip_data)
    if inflated_size is not None:
        updated["InflatedSize"] = inflated_size
    else:
        updated.pop("InflatedSize", None)

    return stored, updated


def build_tld(
    mip_buffers: list[bytes],
    txtr_meta: dict,
) -> tuple[bytes, list[dict]]:
    """Rebuild the .tld binary from raw BC7 mip buffers.

    Parameters
    ----------
    mip_buffers:
        List of raw BC7 byte strings, indexed by mip level (mip_buffers[0] =
        full-resolution mip 0, mip_buffers[1] = half-res, …).
    txtr_meta:
        The inner metadata dict from read_txtr() (not the wrapper).

    Returns
    -------
    tld_bytes:
        Complete new .tld file contents.
    updated_segments:
        Segment list with refreshed FileOffset/FileSize/InflatedSize/MemorySize.
    """
    segments: list[dict] = txtr_meta.get("Segments", [])
    if not segments:
        raise ValueError("txtr_meta contains no Segments.")

    pieces: list[bytes] = []
    updated_segments: list[dict] = []
    file_offset = 0

    for seg in segments:
        min_mip: int = seg.get("MinMip", 0)
        max_mip: int = seg.get("MaxMip", 0)

        # Collect raw mip data for this segment (MinMip through MaxMip inclusive).
        chunk = b"".join(mip_buffers[m] for m in range(min_mip, max_mip + 1))

        stored, updated = _build_segment(seg, chunk)
        updated["FileOffset"] = file_offset
        # Preserve MemoryOffset from original (VRAM layout controlled by game engine).
        updated["MemoryOffset"] = seg.get("MemoryOffset", 0)

        pieces.append(stored)
        updated_segments.append(updated)
        file_offset += len(stored)

    tld_bytes = b"".join(pieces)
    return tld_bytes, updated_segments


# ---------------------------------------------------------------------------
# Diagnostic helper
# ---------------------------------------------------------------------------

# Minimal DDS header constants (first 128 bytes + optional 20-byte DX10 ext).
_DDS_MAGIC = b"DDS "
_DDS_HEADER_SIZE = 124        # DDSURFACEDESC2 size (excludes 4-byte magic)
_DX10_DXGI_FORMAT_NAMES: dict[int, str] = {
    98: "BC7_UNORM",
    99: "BC7_UNORM_SRGB",
    87: "B8G8R8A8_UNORM",
    28: "R8G8B8A8_UNORM",
}

def _parse_dds_header(data: bytes) -> dict:
    """Extract basic fields from a DDS file's header bytes."""
    import struct
    if data[:4] != _DDS_MAGIC:
        raise ValueError(f"Not a DDS file (magic={data[:4]!r})")
    # DDSURFACEDESC2 starts at offset 4
    # Offsets relative to byte 4:
    #   0  dwSize, 4 dwFlags, 8 dwHeight, 12 dwWidth, 16 dwPitchOrLinearSize,
    #  20 dwDepth, 24 dwMipMapCount ...
    hdr = data[4: 4 + _DDS_HEADER_SIZE]
    height   = struct.unpack_from("<I", hdr,  8)[0]
    width    = struct.unpack_from("<I", hdr, 12)[0]
    mips     = struct.unpack_from("<I", hdr, 24)[0]
    # DDPF starts at offset 76 within the header struct
    pf_flags = struct.unpack_from("<I", hdr, 80)[0]
    pf_fourcc = hdr[84:88]

    fmt = "unknown"
    header_bytes = 128
    if pf_fourcc == b"DX10":
        # DX10 extension: 20 bytes after the 128-byte header
        dx10 = data[128:148]
        dxgi_fmt = struct.unpack_from("<I", dx10, 0)[0]
        fmt = _DX10_DXGI_FORMAT_NAMES.get(dxgi_fmt, f"DXGI#{dxgi_fmt}")
        header_bytes = 148

    return {
        "width": width,
        "height": height,
        "mips": max(1, mips),
        "format": fmt,
        "header_bytes": header_bytes,
        "pixel_data_bytes": len(data) - header_bytes,
    }


def diagnose_compression(texture_path: str | Path, txtr_meta: dict) -> None:
    """Print a diagnosis for a texture binary (*.tld or *.dds).

    For *.tld  — checks each compressed segment via zlib.decompress.
    For *.dds  — validates DDS header fields against the .txtr metadata
                 and reports expected vs actual BC7 pixel data size.

    Usage::

        from nba2k_editor.assets.logo_patcher.iff_utils import (
            unpack_iff, read_txtr, find_texture_binary_path
        )
        from nba2k_editor.assets.logo_patcher.tld_utils import diagnose_compression

        tmp = unpack_iff("path/to/logo_024.iff")
        meta = read_txtr(tmp)
        bin_path, kind = find_texture_binary_path(tmp)
        diagnose_compression(bin_path, meta)
    """
    texture_path = Path(texture_path)
    suffix = texture_path.suffix.lower()
    raw = texture_path.read_bytes()

    print(f"\nDiagnosing: {texture_path.name}  ({len(raw)} bytes)")
    print(f"Binary type: {suffix.lstrip('.')}")

    # ── DDS branch ───────────────────────────────────────────────────────────
    if suffix == ".dds":
        try:
            info = _parse_dds_header(raw)
        except Exception as exc:
            print(f"  ERROR parsing DDS header: {exc}")
            return

        print(f"  DDS header:  {info['width']}×{info['height']}  "
              f"mips={info['mips']}  format={info['format']}  "
              f"header_bytes={info['header_bytes']}")

        w_meta  = int(txtr_meta.get("Width",  0))
        h_meta  = int(txtr_meta.get("Height", 0))
        m_meta  = int(txtr_meta.get("Mips",   0))
        f_meta  = str(txtr_meta.get("Format", ""))

        mismatches: list[str] = []
        if w_meta and info["width"]  != w_meta: mismatches.append(f"Width {info['width']} != txtr {w_meta}")
        if h_meta and info["height"] != h_meta: mismatches.append(f"Height {info['height']} != txtr {h_meta}")
        if m_meta and info["mips"]   != m_meta: mismatches.append(f"Mips {info['mips']} != txtr {m_meta}")
        if f_meta and info["format"] != f_meta: mismatches.append(f"Format {info['format']} != txtr {f_meta}")

        if mismatches:
            for m in mismatches:
                print(f"  WARNING: {m}")
        else:
            print("  Metadata matches .txtr ✓")

        # Validate expected pixel data size vs actual
        expected_px = sum(
            bc7_mip_size(info["width"], info["height"], mip)
            for mip in range(info["mips"])
        )
        actual_px = info["pixel_data_bytes"]
        if expected_px == actual_px:
            print(f"  Pixel data size {actual_px} bytes matches expected BC7 layout ✓")
        else:
            print(f"  WARNING: pixel data {actual_px} bytes, expected {expected_px} bytes for BC7 layout")

        print("\nDDS textures are stored raw — no compression to verify.\n")
        return

    # ── TLD branch ───────────────────────────────────────────────────────────
    segments: list[dict] = txtr_meta.get("Segments", [])
    print(f"  Segments in .txtr: {len(segments)}\n")
    all_ok = True
    for i, seg in enumerate(segments):
        off     = seg.get("FileOffset", 0)
        size    = seg.get("FileSize",   0)
        inflated = seg.get("InflatedSize")
        min_mip  = seg.get("MinMip", "?")
        max_mip  = seg.get("MaxMip", "?")
        chunk   = raw[off : off + size]
        if inflated is not None:
            try:
                decompressed = zlib.decompress(chunk)
                ok = len(decompressed) == inflated
                status = (
                    f"OK  (inflated {len(decompressed)} == expected {inflated})"
                    if ok else
                    f"SIZE MISMATCH (got {len(decompressed)}, expected {inflated})"
                )
                if not ok:
                    all_ok = False
            except Exception as exc:
                status = f"FAILED – {exc}"
                all_ok = False
            print(f"  Seg {i}  mip {min_mip}-{max_mip}  "
                  f"off={off:#010x}  stored={size}  COMPRESSED  → {status}")
        else:
            print(f"  Seg {i}  mip {min_mip}-{max_mip}  "
                  f"off={off:#010x}  stored={size}  RAW")

    verdict = (
        "All compressed segments decompressed successfully ✓"
        if all_ok else
        "WARNING: one or more segments failed — compression is NOT plain zlib"
    )
    print(f"\n{verdict}\n")
