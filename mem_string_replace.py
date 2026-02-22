"""
One-off: scan NBA 2K26 live memory for a UTF-16LE string and overwrite it.

Usage:
    python mem_string_replace.py [--dry-run]
"""
from __future__ import annotations

import argparse
import ctypes
import sys
from ctypes import wintypes

# ── Win32 plumbing ──────────────────────────────────────────────────────────

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

PROCESS_ALL_ACCESS = 0x001F0FFF
TH32CS_SNAPPROCESS = 0x00000002

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize",              wintypes.DWORD),
        ("cntUsage",            wintypes.DWORD),
        ("th32ProcessID",       wintypes.DWORD),
        ("th32DefaultHeapID",   ctypes.c_uint64),
        ("th32ModuleID",        wintypes.DWORD),
        ("cntThreads",          wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase",      wintypes.LONG),
        ("dwFlags",             wintypes.DWORD),
        ("szExeFile",           wintypes.WCHAR * 260),
    ]

MEM_COMMIT  = 0x1000
PAGE_NOACCESS       = 0x01
PAGE_GUARD          = 0x100
PAGE_EXECUTE        = 0x10   # not readable as data

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress",       ctypes.c_uint64),
        ("AllocationBase",    ctypes.c_uint64),
        ("AllocationProtect", wintypes.DWORD),
        ("__alignment1",      wintypes.DWORD),
        ("RegionSize",        ctypes.c_uint64),
        ("State",             wintypes.DWORD),
        ("Protect",           wintypes.DWORD),
        ("Type",              wintypes.DWORD),
        ("__alignment2",      wintypes.DWORD),
    ]

VirtualQueryEx = kernel32.VirtualQueryEx
VirtualQueryEx.argtypes = [
    wintypes.HANDLE, ctypes.c_uint64,
    ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t,
]
VirtualQueryEx.restype = ctypes.c_size_t

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [
    wintypes.HANDLE, ctypes.c_uint64, ctypes.c_void_p,
    ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t),
]
ReadProcessMemory.restype = wintypes.BOOL

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = [
    wintypes.HANDLE, ctypes.c_uint64, ctypes.c_void_p,
    ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t),
]
WriteProcessMemory.restype = wintypes.BOOL

# ── helpers ─────────────────────────────────────────────────────────────────

def find_pid(exe_name: str) -> int | None:
    snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == ctypes.c_void_p(-1).value:
        return None
    entry = PROCESSENTRY32W()
    entry.dwSize = ctypes.sizeof(entry)
    if kernel32.Process32FirstW(snap, ctypes.byref(entry)):
        while True:
            if entry.szExeFile.lower() == exe_name.lower():
                pid = entry.th32ProcessID
                kernel32.CloseHandle(snap)
                return pid
            if not kernel32.Process32NextW(snap, ctypes.byref(entry)):
                break
    kernel32.CloseHandle(snap)
    return None


def scan_and_replace(
    hproc: wintypes.HANDLE,
    needle: bytes,
    replacement: bytes,
    *,
    dry_run: bool = False,
) -> int:
    """Scan all committed readable regions; return number of patches applied."""
    assert len(replacement) == len(needle), "replacement must equal needle length"

    hits = 0
    addr = 0
    mbi  = MEMORY_BASIC_INFORMATION()
    chunk_size = 128 * 1024  # 128 KB slabs

    while True:
        ret = VirtualQueryEx(hproc, addr, ctypes.byref(mbi), ctypes.sizeof(mbi))
        if ret == 0:
            break

        region_end = mbi.BaseAddress + mbi.RegionSize

        if (
            mbi.State == MEM_COMMIT
            and not (mbi.Protect & PAGE_NOACCESS)
            and not (mbi.Protect & PAGE_GUARD)
        ):
            # Read in slabs to avoid huge allocations / partial-read failures
            rbase = mbi.BaseAddress
            while rbase < region_end:
                rlen = min(chunk_size, region_end - rbase)
                buf  = ctypes.create_string_buffer(rlen)
                nread = ctypes.c_size_t(0)
                ok = ReadProcessMemory(hproc, rbase, buf, rlen, ctypes.byref(nread))
                if ok and nread.value >= len(needle):
                    data = buf.raw[: nread.value]
                    offset = 0
                    while True:
                        idx = data.find(needle, offset)
                        if idx == -1:
                            break
                        abs_addr = rbase + idx
                        print(f"  FOUND at 0x{abs_addr:016X}", end="")
                        if dry_run:
                            print("  (dry-run, skipping write)")
                        else:
                            wbuf  = ctypes.create_string_buffer(replacement)
                            nwrit = ctypes.c_size_t(0)
                            wok   = WriteProcessMemory(
                                hproc, abs_addr, wbuf,
                                len(replacement), ctypes.byref(nwrit)
                            )
                            if wok and nwrit.value == len(replacement):
                                print("  -> PATCHED")
                                hits += 1
                            else:
                                err = ctypes.get_last_error()
                                print(f"  -> WRITE FAILED (err={err})")
                        offset = idx + len(needle)
                rbase += rlen

        addr = region_end
        if addr >= 0x7FFF_FFFF_FFFF:  # stay in user-mode VA space
            break

    return hits


# ── main ────────────────────────────────────────────────────────────────────

SEARCH_STR  = "Klassische NBA-Teams"
REPLACE_STR = "ProA"
EXE_NAME    = "NBA2K26.exe"


def main() -> None:
    ap = argparse.ArgumentParser(description="Scan NBA 2K26 memory and replace a string.")
    ap.add_argument("--dry-run", action="store_true", help="Find but don't patch.")
    ap.add_argument("--search",  default=SEARCH_STR,  help="UTF-16LE string to find.")
    ap.add_argument("--replace", default=REPLACE_STR, help="UTF-16LE string to write.")
    ap.add_argument("--exe",     default=EXE_NAME,    help="Process exe name.")
    args = ap.parse_args()

    needle_str  = args.search
    replace_str = args.replace

    # Null-pad (not truncate) replacement to match needle byte length
    needle_bytes  = needle_str.encode("utf-16le")
    replace_bytes = replace_str.encode("utf-16le")
    if len(replace_bytes) > len(needle_bytes):
        print(f"ERROR: replacement ({len(replace_bytes)}B) is longer than needle ({len(needle_bytes)}B).")
        sys.exit(1)
    replace_bytes = replace_bytes + b"\x00" * (len(needle_bytes) - len(replace_bytes))

    print(f"Needle  : {needle_str!r}  ({len(needle_bytes)} bytes UTF-16LE)")
    print(f"Replace : {replace_str!r} (padded to {len(replace_bytes)} bytes)")
    print(f"Dry-run : {args.dry_run}")
    print()

    pid = find_pid(args.exe)
    if pid is None:
        print(f"ERROR: '{args.exe}' not found in process list.")
        sys.exit(1)
    print(f"Found {args.exe}  PID={pid}")

    hproc = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not hproc:
        err = ctypes.get_last_error()
        print(f"ERROR: OpenProcess failed (err={err}).  Try running as Administrator.")
        sys.exit(1)

    print("Scanning memory regions...\n")
    hits = scan_and_replace(hproc, needle_bytes, replace_bytes, dry_run=args.dry_run)
    kernel32.CloseHandle(hproc)
    print()
    print(f"Total patches: {hits}")


if __name__ == "__main__":
    main()
