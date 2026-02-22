# Player Base RVA Hunt (NBA2K26)

This is the exact read-only method used to get the Player base RVA when the
normal player-base chain is wrong or returns the All-Star list.

## Summary
We anchor on the known Team table (stable RVA) to pull the 76ers roster
pointers, then back-calculate the **player table base** using the player
stride. After we find the live base, we scan the module for **direct
pointers** to that base and use one of those RVAs in the offsets file.

## Requirements
- Game running and on the roster screen (full roster loaded).
- Correct offsets for:
  - Team base RVA (`base_pointers.Team.address`)
  - `teamSize`
  - `playerSize`
  - Vitals: `Last Name` at `0x0`, `First Name` at `0x28` (or current values).
  - Team Players offsets (0x0, 0x8, 0x10, ...).

## Step-by-step
1) Resolve Team table base.
   - Read QWORD at `module_base + Team_RVA` (`0x7CEC550` in the current build).
   - That value is the Team table base.
   - Team record for 76ers is index 0.

2) Read the 76ers roster pointer list.
   - From the 76ers team record, read the Team Players pointers at offsets
     0x0, 0x8, 0x10, ... (first 15 is enough).

3) Derive the Player table base by voting.
   - For each roster pointer `p`, compute `base = p - idx * playerSize`
     for `idx` in `0..MAX_PLAYERS` (use ~6000).
   - Count votes per base. The real base gets the most votes (usually 15).

4) Verify the base.
   - Read first 15 player names from `base + i * playerSize`.
   - The first names should match the 76ers list, e.g.:
     Tyrese Maxey, V.J. Edgecombe, Kelly Oubre Jr., Paul George,
     Joel Embiid, Quentin Grimes, Andre Drummond, etc.
   - If you see an All-Star list (Brunson/Adebayo/Brown/Mitchell/etc.),
     you are on the wrong table.

5) Convert the live base to a module RVA.
   - Scan the module memory for QWORD values equal to the live base.
   - Each hit is an RVA where the module stores a pointer to the base.
   - Use one of these RVAs as `base_pointers.Player.address` with empty chain.

## Example (this run)
- Team base RVA: `0x7CEC550` (dec 130991440)
- Live player base found by voting: `0x200AF0670` (changes each run)
- Direct module pointers to that base (RVAs):
  - `0x7CEC2F8` (dec 130990840) -- was correct
  - `0x7CEC7E8` (dec 130992104)
  - `0x7D8C068` (dec 131645544)
  - `0x7D8C558` (dec 131646808)
  - `0x7D8E728` (dec 131655464)
  - `0x7D8EC18` (dec 131656728)
  - `0x82711B8` (dec 136778168)

## Offsets file update
Use the chosen RVA as a pointer (single dereference):

```json
"Player": {
  "address": 130990840,
  "chain": []
}
```

Notes:
- `chain: []` means the editor does **one dereference** at `module_base + address`.
- If you set `direct_table: true`, it will skip the dereference (not desired here).

## Troubleshooting
- If the first 15 names are All-Star style, you anchored to the wrong table.
- If names look vertical/junk, check name offsets (Last=0x0, First=0x28).
- If nothing resolves, confirm the editor is loading the offsets file you edited.
