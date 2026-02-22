"""
Base address resolver for NBA2K26 following AGENTS.md.

It attaches to the running NBA2K26.exe, locates roster and draft-class bases
via signature scans, reads the fixed player/team base slots, and derives the
secondary tables (coach/staff, histories, Hall of Fame, name list).

Outputs a concise JSON report to outputs/dynamic_tables.json.

Usage:
    python agents_base_resolver.py
"""

from __future__ import annotations

import ctypes
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

try:
    import psutil
except ImportError:
    print("psutil is required. Install with: pip install psutil", file=sys.stderr)
    sys.exit(1)

PROCESS_NAME = "NBA2K26.exe"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_JSON = OUTPUT_DIR / "dynamic_tables.json"

# Signatures and constants from AGENTS.md
ROSTER_PATTERN = bytes.fromhex("58 63 43 E9 58 63 43")
DRAFT_NBA_PATTERN = bytes.fromhex("00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 96")
DRAFT_WNBA_PATTERN = bytes.fromhex("00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 5A")
ROSTER_POINTER_BACK = 0xE0
DRAFT_POINTER_FORWARD = 0x18
DRAFT_FALLBACK_RVA = 0x6BBFB90
PLAYER_SLOT_RVA = 0x7CEC2B8
TEAM_SLOT_RVA = 0x7CEC510

DERIVED_OFFSETS = {
    "coach_begin": 0x188,
    "coach_end": 0x198,
    "team_history_begin": 0x88,
    "team_history_end": 0x98,
    "nba_history_root": 0x2E8,
    "hall_of_fame_begin": 0x338,
    "hall_of_fame_end": 0x348,
    "name_list_begin": 0x98,
    "name_list_end": 0xA8,
    "career_stats_next_index": 0x12,
}

STRIDES = {
    "player": 1176,
    "team": 5672,
    "jersey": 368,
    "stadium": 4792,
    "coach": 432,
    "career_stats": 64,
    "history": 168,
    "hall_of_fame": 108,
    "name_list": 0x48,
}

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000
PAGE_GUARD = 0x100
READABLE_PROTECT = {
    0x02,  # PAGE_READONLY
    0x04,  # PAGE_READWRITE
    0x08,  # PAGE_WRITECOPY
    0x20,  # PAGE_EXECUTE_READ
    0x40,  # PAGE_EXECUTE_READWRITE
    0x80,  # PAGE_EXECUTE_WRITECOPY
}

# Windows API bindings
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("Psapi.dll", use_last_error=True)

OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [ctypes.c_uint, ctypes.c_bool, ctypes.c_uint]
OpenProcess.restype = ctypes.c_void_p

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [ctypes.c_void_p]
CloseHandle.restype = ctypes.c_bool

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
ReadProcessMemory.restype = ctypes.c_bool

LIST_MODULES_ALL = 0x03


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_ulong),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong),
    ]


class MODULEINFO(ctypes.Structure):
    _fields_ = [
        ("lpBaseOfDll", ctypes.c_void_p),
        ("SizeOfImage", ctypes.c_size_t),
        ("EntryPoint", ctypes.c_void_p),
    ]


VirtualQueryEx = kernel32.VirtualQueryEx
VirtualQueryEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t]
VirtualQueryEx.restype = ctypes.c_size_t


EnumProcessModulesEx = psapi.EnumProcessModulesEx
EnumProcessModulesEx.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.c_ulong,
    ctypes.POINTER(ctypes.c_ulong),
    ctypes.c_uint,
]
EnumProcessModulesEx.restype = ctypes.c_bool

GetModuleInformation = psapi.GetModuleInformation
GetModuleInformation.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.POINTER(MODULEINFO),
    ctypes.c_ulong,
]
GetModuleInformation.restype = ctypes.c_bool

GetModuleFileNameExW = psapi.GetModuleFileNameExW
GetModuleFileNameExW.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint]
GetModuleFileNameExW.restype = ctypes.c_uint


def find_process_pid(exe_name: str = PROCESS_NAME) -> Optional[int]:
    target = exe_name.lower()
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = (proc.info.get("name") or "").lower()
            if name == target:
                return int(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def read_memory(handle: int, address: int, size: int) -> Optional[bytes]:
    if size <= 0:
        return None
    buffer = (ctypes.c_char * size)()
    read = ctypes.c_size_t(0)
    ok = ReadProcessMemory(handle, ctypes.c_void_p(address), buffer, size, ctypes.byref(read))
    if not ok or read.value == 0:
        return None
    return bytes(buffer[: read.value])


def read_u64(handle: int, address: int) -> Optional[int]:
    data = read_memory(handle, address, 8)
    if not data or len(data) < 8:
        return None
    return int.from_bytes(data[:8], byteorder="little", signed=False)


def iter_memory_regions(handle: int, start: int, end: int) -> Iterator[Tuple[int, int, int]]:
    mbi = MEMORY_BASIC_INFORMATION()
    current = start
    while current < end:
        result = VirtualQueryEx(
            handle,
            ctypes.c_void_p(current),
            ctypes.byref(mbi),
            ctypes.sizeof(mbi),
        )
        if not result:
            current += 0x1000
            continue
        base = int(mbi.BaseAddress or 0)
        size = int(mbi.RegionSize)
        if size <= 0:
            current += 0x1000
            continue
        region_end = base + size
        state = int(mbi.State)
        protect = int(mbi.Protect)
        base_protect = protect & 0xFF
        readable = state == MEM_COMMIT and base_protect in READABLE_PROTECT and not (protect & PAGE_GUARD)
        if readable:
            usable_start = max(base, start)
            usable_end = min(region_end, end)
            if usable_end > usable_start:
                yield usable_start, usable_end - usable_start, protect
        current = max(region_end, current + 0x1000)


def scan_pattern_in_module(handle: int, module_base: int, module_size: int, pattern: bytes) -> Optional[int]:
    if not pattern:
        return None
    pat_len = len(pattern)
    carry = b""
    module_end = module_base + module_size
    for region_base, region_size, _ in iter_memory_regions(handle, module_base, module_end):
        buf = read_memory(handle, region_base, region_size)
        if not buf:
            continue
        data = carry + buf
        idx = data.find(pattern)
        if idx != -1:
            return region_base - len(carry) + idx
        carry = data[-(pat_len - 1) :] if pat_len > 1 and len(data) >= pat_len - 1 else b""
    return None


def get_main_module_info(handle: int) -> Optional[dict]:
    arr_size = 512
    modules = (ctypes.c_void_p * arr_size)()
    needed = ctypes.c_ulong(0)
    if not EnumProcessModulesEx(handle, modules, ctypes.sizeof(modules), ctypes.byref(needed), LIST_MODULES_ALL):
        return None
    module_count = needed.value // ctypes.sizeof(ctypes.c_void_p)
    if module_count == 0:
        return None
    h_mod = modules[0]
    info = MODULEINFO()
    if not GetModuleInformation(handle, h_mod, ctypes.byref(info), ctypes.sizeof(info)):
        return None
    path_buf = ctypes.create_unicode_buffer(260)
    length = GetModuleFileNameExW(handle, h_mod, path_buf, len(path_buf))
    return {
        "base": int(info.lpBaseOfDll or 0),
        "size": int(info.SizeOfImage),
        "path": path_buf.value if length else "",
    }


def addr_info(value: Optional[int], module_base: int, module_size: int) -> Optional[dict]:
    if value is None:
        return None
    info: dict[str, object] = {"abs": f"0x{int(value):X}"}
    if module_base <= value < module_base + module_size:
        rva = value - module_base
        info["rva"] = rva
        info["rva_hex"] = f"0x{rva:X}"
    return info


def calc_count(begin: Optional[int], end: Optional[int], stride: int) -> Optional[int]:
    if begin is None or end is None or end <= begin or stride <= 0:
        return None
    return (end - begin) // stride


def resolve_all() -> dict:
    pid = find_process_pid()
    if not pid:
        raise RuntimeError(f"{PROCESS_NAME} is not running.")

    handle = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not handle:
        raise RuntimeError("Failed to open process for reading.")

    try:
        module = get_main_module_info(handle)
        if not module:
            raise RuntimeError("Could not read main module information.")
        base = module["base"]
        size = module["size"]

        roster_sig_addr = scan_pattern_in_module(handle, base, size, ROSTER_PATTERN)
        roster_ptr_addr = roster_sig_addr - ROSTER_POINTER_BACK if roster_sig_addr else None
        roster_base = read_u64(handle, roster_ptr_addr) if roster_ptr_addr else None

        draft_info = {}
        for key, pat in (("nba", DRAFT_NBA_PATTERN), ("wnba", DRAFT_WNBA_PATTERN)):
            sig_addr = scan_pattern_in_module(handle, base, size, pat)
            ptr_addr = sig_addr + DRAFT_POINTER_FORWARD if sig_addr else None
            ptr_val = read_u64(handle, ptr_addr) if ptr_addr else None
            draft_info[key] = {
                "signature_address": addr_info(sig_addr, base, size),
                "pointer_address": addr_info(ptr_addr, base, size),
                "base": addr_info(ptr_val, base, size),
                "source": "signature" if ptr_val else None,
            }

        for key in ("nba", "wnba"):
            if draft_info[key]["base"] is None:
                fallback_addr = base + DRAFT_FALLBACK_RVA
                fallback_val = read_u64(handle, fallback_addr)
                draft_info[key].update(
                    {
                        "signature_address": draft_info[key]["signature_address"],
                        "pointer_address": addr_info(fallback_addr, base, size),
                        "base": addr_info(fallback_val, base, size),
                        "source": "fallback",
                    }
                )

        player_slot_addr = base + PLAYER_SLOT_RVA
        team_slot_addr = base + TEAM_SLOT_RVA
        player_base = read_u64(handle, player_slot_addr)
        team_base = read_u64(handle, team_slot_addr)

        derived = {}
        if roster_base is not None:
            derived["coach"] = {
                "begin": addr_info(read_u64(handle, roster_base + DERIVED_OFFSETS["coach_begin"]), base, size),
                "end": addr_info(read_u64(handle, roster_base + DERIVED_OFFSETS["coach_end"]), base, size),
                "stride": STRIDES["coach"],
            }
            derived["team_history"] = {
                "begin": addr_info(read_u64(handle, roster_base + DERIVED_OFFSETS["team_history_begin"]), base, size),
                "end": addr_info(read_u64(handle, roster_base + DERIVED_OFFSETS["team_history_end"]), base, size),
                "stride": STRIDES["history"],
            }
            derived["nba_history_root"] = {
                "base": addr_info(read_u64(handle, roster_base + DERIVED_OFFSETS["nba_history_root"]), base, size),
                "stride": STRIDES["history"],
            }
            derived["hall_of_fame"] = {
                "begin": addr_info(read_u64(handle, roster_base + DERIVED_OFFSETS["hall_of_fame_begin"]), base, size),
                "end": addr_info(read_u64(handle, roster_base + DERIVED_OFFSETS["hall_of_fame_end"]), base, size),
                "stride": STRIDES["hall_of_fame"],
            }
            derived["name_list"] = {
                "begin": addr_info(read_u64(handle, roster_base + DERIVED_OFFSETS["name_list_begin"]), base, size),
                "end": addr_info(read_u64(handle, roster_base + DERIVED_OFFSETS["name_list_end"]), base, size),
                "stride": STRIDES["name_list"],
            }
            derived["career_stats_next_index_offset"] = DERIVED_OFFSETS["career_stats_next_index"]

            for key, entry in list(derived.items()):
                if not isinstance(entry, dict):
                    continue
                begin = entry.get("begin", {})
                end = entry.get("end", {})
                stride = entry.get("stride")
                if begin and end and stride and isinstance(begin, dict) and isinstance(end, dict):
                    b_abs = int(begin.get("abs", "0"), 16) if begin.get("abs") else None
                    e_abs = int(end.get("abs", "0"), 16) if end.get("abs") else None
                    if b_abs is not None and e_abs is not None:
                        entry["count"] = calc_count(b_abs, e_abs, stride)
        else:
            derived["error"] = "roster_base_addr unresolved; derived pointers unavailable."

        return {
            "meta": {
                "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                "pid": pid,
                "process": PROCESS_NAME,
                "source": "AGENTS.md (Jan 27 2026 patch)",
            },
            "roster": {
                "signature_address": addr_info(roster_sig_addr, base, size),
                "pointer_address": addr_info(roster_ptr_addr, base, size),
                "base": addr_info(roster_base, base, size),
            },
            "draft_class": draft_info,
            "static_slots": {
                "player_slot_address": addr_info(player_slot_addr, base, size),
                "player_base": addr_info(player_base, base, size),
                "team_slot_address": addr_info(team_slot_addr, base, size),
                "team_base": addr_info(team_base, base, size),
            },
            "derived": derived,
            "strides": STRIDES,
        }
    finally:
        if handle:
            CloseHandle(handle)


def main() -> None:
    start = time.time()
    try:
        result = resolve_all()
    except Exception as exc:  # noqa: BLE001 - narrow scope runtime surface
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    duration = time.time() - start
    result["meta"]["elapsed_sec"] = round(duration, 3)
    OUTPUT_JSON.write_text(json.dumps(result, indent=2))

    def show_abs(entry: object) -> str:
        if isinstance(entry, dict):
            return entry.get("abs", "None")
        return str(entry)

    roster_base = result["roster"]["base"]
    player_base = result["static_slots"]["player_base"]
    team_base = result["static_slots"]["team_base"]
    draft_nba = result["draft_class"]["nba"]["base"]
    draft_wnba = result["draft_class"]["wnba"]["base"]

    print(f"Done in {duration:.2f}s")
    print(f"Roster base: {show_abs(roster_base)}")
    print(f"Player base: {show_abs(player_base)} | Team base: {show_abs(team_base)}")
    print(f"Draft class NBA: {show_abs(draft_nba)} | WNBA: {show_abs(draft_wnba)}")
    print(f"Wrote {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
