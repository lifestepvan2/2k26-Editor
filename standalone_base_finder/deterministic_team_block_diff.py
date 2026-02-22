"""
Deterministic team-block snapshot diff with exact layout classification.

No ranking/scoring is used. Each changed pointer payload is classified by
strict known layouts:
  - player_table: stride 1176, UTF-16 names at +0x00/+0x28
  - team_record_table: stride 64, constants at +0x04/+0x3C and team_low32 @ +0x00
  - unknown_layout: does not match known deterministic layouts

Outputs:
  - outputs/deterministic_team_block_diff_<A>_to_<B>.json
  - outputs/deterministic_team_block_diff_<A>_to_<B>.md
"""

from __future__ import annotations

import argparse
import base64
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_int(text: Any, default: Optional[int] = None) -> Optional[int]:
    if text is None:
        return default
    if isinstance(text, int):
        return text
    s = str(text).strip()
    if not s:
        return default
    try:
        base = 16 if s.lower().startswith("0x") else 10
        return int(s, base)
    except Exception:
        return default


def decode_b64(raw: Any) -> bytes:
    if not raw:
        return b""
    try:
        return base64.b64decode(str(raw), validate=False)
    except Exception:
        return b""


def read_u32le(buf: bytes, off: int) -> int:
    if off + 4 > len(buf):
        return 0
    return int.from_bytes(buf[off : off + 4], byteorder="little", signed=False)


def decode_utf16z(data: bytes) -> str:
    try:
        s = data.decode("utf-16le", errors="ignore")
    except Exception:
        return ""
    return s.split("\x00", 1)[0].strip()


def looks_like_name(text: str) -> bool:
    if len(text) < 2 or len(text) > 24:
        return False
    ok = 0
    for ch in text:
        if ch.isalpha() or ch in " .'-":
            ok += 1
    return ok >= max(2, len(text) - 1)


def is_player_table(payload: bytes) -> bool:
    stride = 1176
    if len(payload) < stride * 2:
        return False
    good = 0
    for idx in range(3):
        base = idx * stride
        last = decode_utf16z(payload[base : base + 40])
        first = decode_utf16z(payload[base + 0x28 : base + 0x28 + 40])
        if looks_like_name(first) and looks_like_name(last):
            good += 1
    return good >= 2


def is_team_record_table(payload: bytes, team_low32: Optional[int]) -> bool:
    row_size = 64
    if len(payload) < row_size * 8:
        return False
    rows = min(64, len(payload) // row_size)
    const_hits = 0
    low32_hits = 0
    for i in range(rows):
        row = payload[i * row_size : (i + 1) * row_size]
        if read_u32le(row, 4) == 1 and read_u32le(row, 60) == 0:
            const_hits += 1
        if team_low32 is not None and read_u32le(row, 0) == team_low32:
            low32_hits += 1
    const_ratio = const_hits / float(max(1, rows))
    low32_ratio = low32_hits / float(max(1, rows)) if team_low32 is not None else 0.0
    return const_ratio >= 0.85 and (team_low32 is None or low32_ratio >= 0.70)


def classify_payload(payload: bytes, team_low32: Optional[int]) -> str:
    if not payload:
        return "no_payload"
    if is_player_table(payload):
        return "player_table"
    if is_team_record_table(payload, team_low32):
        return "team_record_table"
    return "unknown_layout"


def load_snapshot(path: Path) -> Dict[Tuple[int, int], Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("entries", [])
    out: Dict[Tuple[int, int], Dict[str, Any]] = {}
    for e in entries:
        if not isinstance(e, dict):
            continue
        team_idx = parse_int(e.get("team_index"))
        team_off = parse_int(e.get("team_offset"))
        if team_idx is None or team_off is None:
            continue
        out[(team_idx, team_off)] = e
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Deterministic team-block snapshot diff with exact layout filters.")
    p.add_argument("--snapshot-a", required=True, help="Path to snapshot A JSON.")
    p.add_argument("--snapshot-b", required=True, help="Path to snapshot B JSON.")
    p.add_argument("--label-a", default="A", help="Label for snapshot A.")
    p.add_argument("--label-b", default="B", help="Label for snapshot B.")
    p.add_argument("--out-prefix", default="outputs/deterministic_team_block_diff", help="Output prefix.")
    args = p.parse_args()

    a_path = Path(args.snapshot_a)
    if not a_path.is_absolute():
        a_path = SCRIPT_DIR / a_path
    b_path = Path(args.snapshot_b)
    if not b_path.is_absolute():
        b_path = SCRIPT_DIR / b_path

    idx_a = load_snapshot(a_path)
    idx_b = load_snapshot(b_path)
    keys = sorted(set(idx_a.keys()) | set(idx_b.keys()))

    changed_entries: List[Dict[str, Any]] = []
    unknown_changed: List[Dict[str, Any]] = []
    per_offset_layouts: Dict[int, Counter] = defaultdict(Counter)

    for key in keys:
        a = idx_a.get(key)
        b = idx_b.get(key)
        if not a or not b:
            continue
        sha_a = str(a.get("payload_sha256", ""))
        sha_b = str(b.get("payload_sha256", ""))
        raw_a = str(a.get("raw_value", ""))
        raw_b = str(b.get("raw_value", ""))
        ptr_a = str(a.get("pointer_target", ""))
        ptr_b = str(b.get("pointer_target", ""))

        if sha_a == sha_b and raw_a == raw_b and ptr_a == ptr_b:
            continue

        team_idx = int(key[0])
        team_off = int(key[1])
        low32 = parse_int(a.get("team_address_low32"))
        payload_a = decode_b64(a.get("payload_bytes_b64"))
        payload_b = decode_b64(b.get("payload_bytes_b64"))
        cls_a = classify_payload(payload_a, low32)
        cls_b = classify_payload(payload_b, low32)

        entry = {
            "team_index": team_idx,
            "team_offset": team_off,
            "team_offset_hex": f"0x{team_off:X}",
            "raw_before": raw_a or None,
            "raw_after": raw_b or None,
            "pointer_before": ptr_a or None,
            "pointer_after": ptr_b or None,
            "payload_changed": sha_a != sha_b,
            "class_before": cls_a,
            "class_after": cls_b,
        }
        changed_entries.append(entry)
        per_offset_layouts[team_off][cls_a] += 1
        per_offset_layouts[team_off][cls_b] += 1
        if cls_a == "unknown_layout" or cls_b == "unknown_layout":
            unknown_changed.append(entry)

    offset_summary: List[Dict[str, Any]] = []
    for off, counter in sorted(per_offset_layouts.items()):
        dominant = counter.most_common(1)[0][0] if counter else "none"
        total = sum(counter.values())
        unknown_hits = int(counter.get("unknown_layout", 0))
        offset_summary.append(
            {
                "team_offset": off,
                "team_offset_hex": f"0x{off:X}",
                "layout_counts": dict(counter),
                "dominant_layout": dominant,
                "unknown_layout_ratio": round(unknown_hits / float(max(1, total)), 6),
            }
        )

    out = {
        "meta": {
            "timestamp_utc": utc_now_iso(),
            "snapshot_a": str(a_path),
            "snapshot_b": str(b_path),
            "label_a": args.label_a,
            "label_b": args.label_b,
        },
        "summary": {
            "entries_compared": len(keys),
            "changed_entries": len(changed_entries),
            "unknown_layout_changed_entries": len(unknown_changed),
            "offsets_with_changes": len(offset_summary),
            "offsets_with_unknown_layout_changes": len(
                {e["team_offset"] for e in unknown_changed}
            ),
        },
        "offset_summary": offset_summary,
        "changed_entries": changed_entries,
        "unknown_layout_changed_entries": unknown_changed,
    }

    stem = f"{args.out_prefix}_{args.label_a}_to_{args.label_b}"
    out_json = Path(stem + ".json")
    if not out_json.is_absolute():
        out_json = SCRIPT_DIR / out_json
    out_md = out_json.with_suffix(".md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Deterministic Team Block Diff")
    lines.append("")
    lines.append(f"- Snapshot A: `{a_path}`")
    lines.append(f"- Snapshot B: `{b_path}`")
    lines.append(f"- Changed entries: `{len(changed_entries)}`")
    lines.append(f"- Unknown-layout changed entries: `{len(unknown_changed)}`")
    lines.append("")
    lines.append("## Offsets With Changes")
    if offset_summary:
        lines.append("| Team Offset | Dominant Layout | Unknown Ratio | Layout Counts |")
        lines.append("|---:|---|---:|---|")
        for row in offset_summary:
            lines.append(
                "| `0x{off:X}` | {dom} | {ur:.3f} | `{counts}` |".format(
                    off=int(row["team_offset"]),
                    dom=row["dominant_layout"],
                    ur=float(row["unknown_layout_ratio"]),
                    counts=row["layout_counts"],
                )
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Unknown Layout Changes")
    if unknown_changed:
        for e in unknown_changed:
            lines.append(
                "- team[{t}] offset=`0x{o:X}` class_before=`{cb}` class_after=`{ca}`".format(
                    t=int(e["team_index"]),
                    o=int(e["team_offset"]),
                    cb=e["class_before"],
                    ca=e["class_after"],
                )
            )
    else:
        lines.append("- None")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_md}")
    print(f"Changed entries: {len(changed_entries)}")
    print(f"Unknown-layout changed entries: {len(unknown_changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
