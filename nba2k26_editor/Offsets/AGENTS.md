# Base Discovery (NBA2K26) – Self‑Contained Guide

This doc explains, end to end, how runtime base addresses are located for players, teams, draft classes, staff/coaches, stadium/history tables, and related arrays—without relying on any repository paths or filenames.

## Prerequisites
- The game process `NBA2K26.exe` must be running.
- You need a way to:
  1) Read the process module base address and size.
  2) Read arbitrary bytes from the module.
  3) Read 8‑byte little‑endian pointers from process memory.
  Tools such as a Python script with `pymem`, or a CE-style memory scanner, are sufficient.

## Step 1 — Roster base (players root)
1) Scan the game module bytes for the 7‑byte signature:  
   `58 63 43 E9 58 63 43`
2) When found, move **back** 0xE0 bytes (decimal 224) from the start of that match.
3) Read an 8‑byte little‑endian pointer at that address.  
   The value is `roster_base_addr`. All other roster-derived pointers hang off this anchor.

## Step 2 — Draft class base
Two signatures exist; each is followed by the same pointer layout:
- NBA pattern:  `00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 96`
- WNBA pattern: `00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 5A`
Process:
1) Find either pattern in the module image.
2) From the start of the matched bytes, move **forward** 0x18 bytes (decimal 24).
3) Read the 8‑byte little‑endian pointer there; that is the draft‑class base for the matched league.
Fallback if no pattern is found: use `module_base + 0x6BBFB90` as the draft‑class base (module_base is the load address of `NBA2K26.exe`).

## Step 3 — Static base slots for players and teams
These are fixed absolute addresses inside the module:
- Player table slot: `0x7CEC2B8` (decimal 130,990,776)
- Team table slot:   `0x7CEC510` (decimal 130,991,376)
Read 8‑byte little‑endian values at those addresses; the pointed-to values are the actual player and team base pointers. (Chains are empty—no extra deref hops.)

## Step 4 — Derived pointers relative to roster_base_addr
Once `roster_base_addr` is known, these offsets yield other collections:
- Coach/Staff array: begin pointer at `roster_base_addr + 0x188`; end pointer at `+0x198`; stride 432.
- Team history array: begin pointer at `roster_base_addr + 0x88`; end pointer at `+0x98`; stride 168.
- NBA history root: pointer at `roster_base_addr + 0x2E8`; stride 168.
- Hall of Fame table: base pointer at `roster_base_addr + 0x338`; end pointer at `+0x348`; stride 108.
- Name list (“From” helper): begin pointer at `roster_base_addr + 0x98`; end pointer at `+0xA8`; entry stride `0x48`. Each entry’s ASCII name starts at offset 0 and is null‑terminated (max length 40).
- Career stats “next index”: offset `0x12` inside each career-stats record; career-stats stride 64.

## Step 5 — Strides for indexed access
- Player: 1176
- Team: 5672
- Jersey: 368
- Stadium: 4792
- Coach/Staff: 432
- Career stats: 64
- History: 168
- Hall of Fame: 108
With a base pointer and an entity index, compute `entity_addr = base + index * stride`.

## Step 6 — Practical flow to resolve everything
1) Attach to `NBA2K26.exe`; record `module_base` and `SizeOfImage`.
2) Locate `roster_base_addr` using the signature/offset method (Step 1).
3) Resolve draft class base(s) via signatures or fallback (Step 2).
4) Read player and team bases directly from the static slots (Step 3).
5) From `roster_base_addr`, compute or read the derived arrays and their bounds (Step 4).
6) Use the stride table (Step 5) to index into any of the arrays once their base pointers are known.

## Troubleshooting tips
- If the roster signature is not found, re-check that you scanned the full module image and that the game version matches the January 27, 2026 patch.
- If the draft patterns fail, rely on the fallback `module_base + 0x6BBFB90`.
- When array begin/end pointers look null, ensure you resolved `roster_base_addr` correctly and that you’re reading 8 bytes with little‑endian order.
