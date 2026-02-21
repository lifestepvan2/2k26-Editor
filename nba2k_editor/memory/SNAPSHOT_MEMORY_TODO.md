# TODO: Snapshot Memory / Offline Development Mode

## Goal

Allow the editor to run fully without a live `NBA2K26.exe` process by replaying
a previously captured binary snapshot of process memory. This is primarily useful
for:

- **Offset development after a game patch** — test against known-good data
  without waiting for updated offsets to work.
- **Automated tests** — `test_live_*` tests currently require the game running.
  With a snapshot they can run in CI.
- **General development** — iterate on UI, parsing logic, field decoding, etc.
  without launching 2K.

---

## Architecture

### Why It's Clean

`GameMemory.read_bytes(addr: int, length: int) -> bytes` (in `game_memory.py`) is
the **only** method that touches `ReadProcessMemory`. All player/team/field
parsing calls only this one method. Swapping it out gives full pipeline coverage.

---

## Implementation Plan

### Step 1 — Capture Script  (`memory/snapshot_capture.py`)

Run this **once** with the game running and offsets working. It uses the live
`GameMemory` to dump every memory region the editor actually reads.

```
nba2k_editor/memory/snapshots/
    <name>.bin      ← concatenated raw bytes of all captured regions
    <name>.json     ← manifest:
                        base_addr: int          # module base at capture time
                        game_version: str       # from game_info
                        regions: list of
                          { abs_start: int, length: int, file_offset: int }
```

Regions to capture (based on `offsets_league.json` base pointers + sizes):
- `Player` table: `base_addr + Player.address` × `playerSize` × `MAX_PLAYERS`
- `Team` table: `base_addr + Team.address` × `teamSize` × 30
- `Staff` table
- `Stadium` table
- `Jersey` table
- `career_stats` table
- `NBAHistory` / `HallOfFame` tables
- Any pointer-chain intermediate addresses used by `_resolve_pointer_chain`

Total expected size: ~a few MB at current struct sizes.

### Step 2 — `SnapshotGameMemory` class  (`memory/snapshot_memory.py`)

Drop-in replacement for `GameMemory`:

```python
class SnapshotGameMemory:
    """Replays a captured binary snapshot in place of live ReadProcessMemory."""

    def __init__(self, snapshot_dir: str | Path, name: str = "default"):
        # loads <name>.json + <name>.bin
        ...

    # --- API must match GameMemory exactly ---

    @property
    def base_addr(self) -> int:
        return self._manifest["base_addr"]

    @property
    def pid(self) -> int:
        return 0   # sentinel

    def attach(self) -> None:
        pass   # no-op

    def read_bytes(self, addr: int, length: int) -> bytes:
        # look up addr in self._regions (sorted list), return slice from .bin
        # raise RuntimeError if addr+length is not covered (same as live)
        ...

    def write_bytes(self, addr: int, data: bytes) -> None:
        # optionally apply writes into an in-memory overlay dict
        # {abs_addr: bytes} so round-trip write→read tests work
        ...
```

Key detail: all addresses passed to `read_bytes` at runtime are **absolute**
(`base_addr + rva`). The manifest stores `abs_start` per region, so lookup is
a simple range search.

### Step 3 — Wiring

In `entrypoints/gui.py` (and any other entrypoint), replace the `GameMemory`
construction with a factory:

```python
# core/memory_factory.py
import os
from pathlib import Path

def make_game_memory(module_name: str):
    snapshot_path = os.environ.get("NBA2K_SNAPSHOT")
    if snapshot_path:
        from ..memory.snapshot_memory import SnapshotGameMemory
        return SnapshotGameMemory(snapshot_path)
    from ..memory.game_memory import GameMemory
    return GameMemory(module_name)
```

Usage in `gui.py`:
```python
mem = make_game_memory(MODULE_NAME)
```

Activation:
```powershell
$env:NBA2K_SNAPSHOT = "C:\path\to\snapshots\2026-02-16"
python -m nba2k_editor
```

Or add a `--snapshot <dir>` CLI flag to `__main__.py` as an alternative.

### Step 4 — Snapshot Aware Tests

Move `test_live_tyrese_maxey_stats_alignment.py` and similar tests from
"requires live process" to "requires snapshot fixture". Add a pytest fixture:

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def snapshot_memory():
    path = os.environ.get("NBA2K_SNAPSHOT")
    if not path:
        pytest.skip("NBA2K_SNAPSHOT not set")
    from nba2k_editor.memory.snapshot_memory import SnapshotGameMemory
    return SnapshotGameMemory(path)
```

---

## Files to Create / Modify

| File | Action |
|------|--------|
| `memory/snapshot_capture.py` | **Create** — capture script |
| `memory/snapshot_memory.py` | **Create** — `SnapshotGameMemory` class |
| `memory/snapshots/.gitignore` | **Create** — ignore `*.bin`, keep `*.json` manifests |
| `core/memory_factory.py` | **Create** — factory function |
| `entrypoints/gui.py` | **Modify** — use `make_game_memory()` |
| `tests/conftest.py` | **Modify** — add `snapshot_memory` fixture |
| `tests/test_live_*.py` | **Modify** — use fixture, skip if no snapshot |

---

## Gotchas

1. **Pointer chains** — `_resolve_pointer_chain` dereferences intermediate
   addresses. The capture script must follow chains and capture intermediate
   addresses too, not just the final table base.

2. **Snapshot versioning** — store `game_version` from `game_info` in the
   manifest so tests can assert they're running against the right snapshot.

3. **Write overlay** — `write_bytes` can apply to an in-memory dict overlay
   (`{abs_addr: bytes}`) so that write→read round-trips work without corrupting
   the snapshot file.

4. **`base_addr` at capture vs replay** — RVAs are constant per build, but
   `base_addr` (ASLR) changes every launch. The snapshot stores the
   `base_addr` at capture time. At replay time, `GameMemory.base_addr` returns
   this captured value, so all `base_addr + rva` calculations produce the same
   absolute addresses the snapshot contains. No translation needed.

5. **Region gaps** — not all of process memory is captured. If any code path
   calls `read_bytes` for an address outside captured regions, `SnapshotGameMemory`
   should raise a clear error (not silently return zeros) so gaps are obvious.
