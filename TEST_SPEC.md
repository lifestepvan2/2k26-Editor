# Test Specification — NBA 2K26 Editor

## Running the Suite

```bash
# From the repo root (2k26-Editor/)
pytest nba2k26_editor/tests/

# With verbose output
pytest nba2k26_editor/tests/ -v

# With coverage (requires pytest-cov)
pytest nba2k26_editor/tests/ --cov=nba2k26_editor --cov-report=term-missing

# Skip tests that require Dear PyGui (e.g. in headless CI)
pytest nba2k26_editor/tests/ -k "not (dearpygui or DPG)"
```

`conftest.py` at the project root ensures `nba2k26_editor` is on `sys.path`
without needing the package to be pip-installed.

---

## Dependency Matrix

| Dependency | Required by | Installed? |
|---|---|---|
| `pytest` | all tests | optional dev dep |
| `dearpygui` | UI-layer tests | optional; tests skip cleanly without it |
| `openpyxl` | `test_perf_import.py` | optional; test skips without it |
| stdlib only | all other tests | always available |

Several UI test files guard themselves with `pytest.importorskip("dearpygui.dearpygui")` —
they are skipped, not failed, when Dear PyGui is absent. The remaining tests
have zero optional-dependency requirements and should always pass.

---

## Live / Integration Test

`test_live_tyrese_maxey_stats_alignment.py` is the only test that requires a
running game process. It is gated at two levels and will not run in normal CI:

```bash
# Enable the live stats verification
set NBA2K_EDITOR_LIVE_STATS_VERIFY=1
pytest nba2k26_editor/tests/test_live_tyrese_maxey_stats_alignment.py -v
```

- Skip condition 1: `@pytest.mark.skipif(sys.platform != "win32", ...)` — skipped on non-Windows.
- Skip condition 2: `if not _verify_enabled(): pytest.skip(...)` — skipped unless the env var is set.

See the [Live Test section](#live-test-test_live_tyrese_maxey_stats_alignmentpy) below for full detail.

---

## Test File Index

### Core / Offset System

#### `test_offsets_services.py`
**What it tests:** The three-layer offset loading pipeline — `OffsetCache`,
`OffsetResolver`, and `OffsetRepository`.

| Test | Description |
|---|---|
| `test_offset_cache_target_roundtrip` | Cache stores and returns a `CachedOffsetPayload`; `invalidate_target` removes it. |
| `test_offset_resolver_prefers_converted_payload` | Resolver calls `convert_schema` first; falls back to `select_entry` if conversion returns `None`. |
| `test_offset_resolver_require_dict_raises` | `require_dict` raises `OffsetResolveError` when the payload is not a dict. |
| `test_offset_repository_loads_and_caches` | Repository reads a JSON file, returns its contents, and serves a cache hit on the second call. |
| `test_initialize_offsets_applies_explicit_filename_even_when_target_cached` | Passing an explicit `filename` to `initialize_offsets` bypasses a cached target entry. |

**Why it matters for memory work:** Every memory read/write depends on the
offset schema being correctly loaded. These tests guard the loading pipeline
so a refactor of `OffsetRepository` or `OffsetCache` is immediately caught.

---

#### `test_split_offsets_fidelity.py`
**What it tests:** The actual 2K26 JSON offset bundle on disk.

| Test | Description |
|---|---|
| `test_stats_table_categories_are_emitted_without_flat_stats_alias` | Confirms the stats categories are named `Stats - IDs / Season / Career / Awards`, not the old flat `Stats` name. |
| `test_player_stats_relations_link_ids_to_season_only` | Verifies the `player_stats` relation block links `Stats - IDs` → `Stats - Season` with the correct field ordering. |
| `test_parse_report_accounts_for_all_discovered_leaf_fields` | The bundle's `_parse_report` must account for every field: `discovered == emitted + skipped` with zero untracked loss. |

**Why it matters for memory work:** This is the closest thing to a schema
integrity test. If the offset JSON is corrupted or truncated during a rebuild,
these assertions catch it before any memory scan runs.

---

#### `test_strict_offset_mapping.py`
**What it tests:** The `initialize_offsets()` function's ability to populate
the module-level offset constants (`PLAYER_STRIDE`, `TEAM_STRIDE`, etc.) from
synthetic schema data.

| Test (abbreviated) | Description |
|---|---|
| `test_initialize_offsets_populates_player_stride` | A synthetic schema entry for `FIRSTNAME` causes `PLAYER_STRIDE` to be set. |
| `test_initialize_offsets_populates_team_stride` | Same for `TEAM_STRIDE`. |
| `test_initialize_offsets_strict_key_resolve_*` | Various tests verify each `STRICT_OFFSET_FIELD_KEYS` entry is resolved correctly from schema data. |

A `restore_offsets_state` pytest fixture snapshots and restores all offset
constants so tests are fully isolated.

---

### Data Model

#### `test_data_model_category_grouping.py`
**What it tests:** `PlayerDataModel.get_categories_for_super()` — the method
that filters the offset category map down to a specific entity type (Players,
Staff, etc.).

| Test | Description |
|---|---|
| `test_get_categories_for_super_groups_player_categories` | Only categories mapped to "Players" appear; Staff categories are excluded. |

---

#### `test_team_pointer_field_behavior.py`
**What it tests:** The pointer field decode/encode cycle for team pointer
fields in `PlayerDataModel.decode_field_value_from_buffer` and the encode
path.

| Test | Description |
|---|---|
| `test_decode_team_pointer_field_displays_team_name` | A raw 8-byte pointer that lands on a team's memory record is decoded as the team display name ("Lakers"), not a raw hex address. |
| `test_decode_non_team_pointer_field_stays_hex` | The same raw bytes in a non-team pointer field stay as a hex string. |
| `test_encode_team_pointer_field_accepts_team_name` | Passing "Lakers" to the encode path writes the correct pointer value back via `_write_entity_field_typed`. |

**Why it matters for memory work:** This is the core of roster-pointer
integrity. A regression here would silently corrupt team assignments in
memory.

---

#### `test_league_history_probe_validation.py`
**What it tests:** `PlayerDataModel.get_league_records()` skipping logic for
blank rows.

| Test | Description |
|---|---|
| `test_get_league_records_accepts_base_when_first_row_is_blank_but_next_row_has_data` | When row 0 is empty and row 1 contains "Tyrese Maxey", only row 1 is returned. Validates the blank-row probe that determines whether the league table base pointer is valid. |

---

#### `test_perf_data_model.py`
**What it tests:** Performance and lazy initialisation behaviour of
`PlayerDataModel`.

| Test | Description |
|---|---|
| `test_data_model_refresh_perf_harness` | `refresh_players`, `refresh_staff`, and `refresh_stadiums` must complete within `NBA2K_EDITOR_PERF_DATA_MODEL_MAX` seconds (default 5.0). |
| `test_data_model_init_reuses_loaded_offsets_for_same_target` | If offsets are already loaded for the active target, model construction must not call `initialize_offsets` again (no redundant disk I/O). |

---

#### `test_startup_load_order.py`
**What it tests:** That the GUI entrypoint's startup sequence does not trigger
redundant offset initialisation.

| Test | Description |
|---|---|
| `test_model_init_does_not_reinitialize_offsets_for_loaded_target` | With `_offset_config` already populated for `nba2k26.exe`, constructing a `PlayerDataModel` must not call `initialize_offsets` a second time. |

---

### Services Layer

#### `test_io_codec_services.py`
**What it tests:** `IOCodec`, `PlayerService`, and `TeamService`.

| Test | Description |
|---|---|
| `test_io_codec_routes_player_and_team_calls` | `IOCodec.get_player` delegates to the model's player read method; `get_team` to the team read method. |
| `test_services_mark_dirty_on_writes` | `PlayerService.set_field` marks `players` as dirty; `TeamService.set_field` and `set_fields` mark `teams` as dirty. |

---

### UI Layer

#### `test_app_full_editor_child_launch.py`
**What it tests:** `PlayerEditorApp._open_full_editor()` and
`_open_full_team_editor()` / `_open_full_staff_editor()` — the methods that
spawn child-process full editors.

| Test | Description |
|---|---|
| `test_open_full_editor_launches_child_with_player_indices` | Duplicate indices are de-duplicated before being passed to `launch_full_editor_process`. |
| `test_open_full_team_editor_launches_child_with_resolved_team_index` | The display name "Bulls" is resolved to numeric index 3 and passed to the child launcher. |
| `test_open_full_staff_editor_launches_selected_scanned_index` | Staff editor uses the scanned entity index, not the filtered list position. |
| `test_selected_staff_indices_return_scanned_id_not_filtered_position` | Same constraint verified at index resolution level. |
| `test_selected_stadium_indices_return_scanned_id_not_filtered_position` | Same for stadiums. |

---

#### `test_full_editor_entrypoint.py`
**What it tests:** `full_editor.parse_editor_request()` (CLI arg parsing) and
`_open_requested_editor()` (routing to the correct editor class).

| Test | Description |
|---|---|
| `test_parse_editor_request_player_indices` | `--indices 1,7,1` parses to `(1, 7)` with deduplication. |
| `test_parse_editor_request_requires_index_for_team` | Missing `--index` exits with `SystemExit`. |
| `test_open_requested_editor_routes_player` | `editor=player` instantiates `FullPlayerEditor` with correct player list. |
| `test_open_requested_editor_routes_team` | `editor=team, index=3` instantiates `FullTeamEditor` with `(3, "Bulls")`. |

---

#### `test_full_editor_launch.py`
**What it tests:** `build_launch_command()` — the function that constructs the
`subprocess` argument list for launching a child editor.

| Test | Description |
|---|---|
| `test_build_launch_command_source_mode` | Source mode: `[python, "-m", "nba2k26_editor.entrypoints.full_editor", "--editor", "team", "--index", "5"]`. |
| `test_build_launch_command_frozen_mode` | Frozen (PyInstaller) mode: `[sys.executable, "--child-full-editor", "--editor", "staff", "--index", "12"]`. |
| `test_build_launch_command_player_indices_deduplicated` | Negative and duplicate indices are stripped: `[4, 4, 9, -1, 2]` → `"4,9,2"`. |

---

#### `test_full_editor_selective_save.py`
**What it tests:** That full editors (`FullPlayerEditor`, `FullTeamEditor`)
only write fields that have actually changed (dirty-field tracking).

| Test | Description |
|---|---|
| `test_full_player_editor_saves_only_changed_fields` | Only modified field values are flushed to `encode_field_value`; unchanged fields are skipped. |
| `test_full_team_editor_saves_only_changed_team_fields` | Same constraint for team fields. |

---

#### `test_full_player_editor_int_bounds.py`
**What it tests:** Integer input control bounds in `FullPlayerEditor`.

| Test | Description |
|---|---|
| `test_sanitize_input_int_range_clamps_to_dpg_int_bounds` | Extreme bounds (±2^60) are clamped to `_DPG_INT_MIN` / `_DPG_INT_MAX`. |
| `test_add_field_control_caps_large_integer_bit_length` | A 64-bit integer field gets capped to `[0, 999999]` for Dear PyGui compatibility. |

---

#### `test_full_player_editor_stats_slots.py`
**What it tests:** The stats tab preparation logic in
`FullPlayerEditor._prepare_stats_tabs()` — specifically the season slot
selector mechanic and Awards field duplication.

| Test | Description |
|---|---|
| `test_prepare_stats_tabs_keeps_career_and_season_awards_merge` | Awards fields appear in both Career Stats and Season Stats tabs. |
| `test_prepare_stats_tabs_adds_season_slot_selector_and_hides_stats_ids` | `Stats - IDs` category is replaced by a slot dropdown injected at position 0 of Season Stats. |
| `test_load_all_values_async_routes_maxey_season_and_awards_fields_via_selected_slot` | Slot selection routes the correct pointer to each field's decode call. |

---

#### `test_stats_tab_routing.py`
**What it tests:** Higher-level stats tab routing, including the
`_league_pointer_for_category` override for career-stats categories.

| Test | Description |
|---|---|
| `test_prepare_stats_tabs_duplicates_awards_into_career_and_season` | Comprehensive duplication check with `__source_category` annotations. |
| `test_prepare_stats_tabs_replaces_stats_ids_with_season_slot_dropdown` | Detailed assertion on slot def ordering and label generation. |
| `test_league_pointer_for_career_category_uses_career_stats_pointer` | Career stats categories use the `career_stats` pointer key. |

---

#### `test_scan_entrypoint_compat.py`
**What it tests:** `PlayerEditorApp._start_scan()` and `_start_team_scan()` —
the scan flow that refreshes players and populates the team dropdown.

| Test | Description |
|---|---|
| `test_start_scan_wrapper_uses_shared_flow_without_regression` | After scan: `refresh_players` called once, render message is "Scanning players...", team dropdown updated. |
| `test_start_team_scan_wrapper_preserves_pending_selection_behavior` | Pending team selection is applied after the scan completes. |
| `test_start_scan_handles_refresh_exception_gracefully` | `RuntimeError` during `refresh_players` sets an error status but does not propagate. |

---

#### `test_ui_screen_loading_regression.py`
**What it tests:** Regression scenarios for scan, trade, and screen-transition
flows.

| Test (abbreviated) | Description |
|---|---|
| `test_start_scan_*` | Mirrors `test_scan_entrypoint_compat.py` with an extended stub (`run_on_ui_thread` support). |
| `test_build_trade_screen_populates_team_dropdowns` | Trade screen receives the correct team list on construction. |
| `test_confirm_trade_refreshes_team_list` | After trade execution, the team dropdown is updated from the refreshed model. |

---

#### `test_excel_callbacks_regression.py`
**What it tests:** The Excel import/export callback wiring in
`build_excel_screen`.

| Test | Description |
|---|---|
| `test_import_callback_routes_entity_key` | The import button callback fires `_import_excel(entity_key)` with the correct key. |
| `test_export_callback_routes_entity_key` | Same for export. |
| `test_export_finish_handler_resets_progress` | The export-done handler clears the progress bar and shows an info dialog. |

---

### State

#### `test_trade_state.py`
**What it tests:** `TradeState` — the data structure that holds pending trade
transactions.

| Test | Description |
|---|---|
| `test_trade_state_add_and_package_projection` | Adding a transaction correctly populates `outgoing` (from team) and `incoming` (to team). |
| `test_trade_state_prevents_duplicates_and_remove` | Adding the same player twice returns `False`; `remove_transaction(0)` clears it. |
| `test_trade_state_clear_slot` | `clear_slot()` empties all transactions in the current slot. |

---

### Launcher / Entrypoints

#### `test_launch_editor_child_mode.py`
**What it tests:** `nba2k26_editor.launch_editor._run_child_full_editor_if_requested()`.

| Test | Description |
|---|---|
| `test_run_child_full_editor_if_requested_routes_arguments` | When `--child-full-editor` is in argv, strips the flag and calls `full_editor.main` with the remainder. |
| `test_run_child_full_editor_if_requested_returns_false_without_flag` | Without the flag, returns `False` and does nothing. |

---

### Startup / Import Hygiene

#### `test_startup_import_hygiene.py`
**What it tests:** That importing `nba2k26_editor.ui.app` does not
transitively pull in heavyweight dependencies.

| Test | Description |
|---|---|
| `test_ui_app_import_does_not_eager_load_heavy_agent_dependencies` | Runs a subprocess that imports `nba2k26_editor.ui.app` and asserts `torch` and `pandas` are not in `sys.modules`. |

> Note: `torch` is historically associated with the now-removed AI/RL modules;
> this test is retained as general import hygiene for `pandas` and any
> future heavy dependencies.

---

#### `test_perf_startup.py`
**What it tests:** GUI startup latency and redundant offset initialisation.

| Test | Description |
|---|---|
| `test_gui_startup_perf_harness` | `gui.main()` with stubbed DPG completes within `NBA2K_EDITOR_PERF_STARTUP_MAX` seconds (default 5.0). Confirms `gui.main` appears in perf summary. |
| `test_gui_startup_does_not_reinitialize_offsets_in_model` | Offsets are loaded exactly once at the `gui.main` level; `PlayerDataModel.__init__` must not call `initialize_offsets` again. |

---

### Import / Excel

#### `test_perf_import.py`
**What it tests:** Excel import/export performance via `import_excel_workbook`
/ `export_excel_workbook`.

_Requires `openpyxl`; skipped automatically without it._

| Test | Description |
|---|---|
| `test_import_export_perf_harness` | Import + export of a two-row workbook completes within `NBA2K_EDITOR_PERF_IMPORT_MAX` seconds (default 8.0). Reports are validated for row counts and perf keys. |

---

### Live Test

#### `test_live_tyrese_maxey_stats_alignment.py`
**What it tests:** Full end-to-end memory read of Tyrese Maxey's (player
index 0) career statistics across 5 season slots.

**Gate conditions (both must be satisfied to run):**
1. `sys.platform == "win32"`
2. `NBA2K_EDITOR_LIVE_STATS_VERIFY=1` environment variable

**How it works:**
1. Opens the NBA2K26 process via `GameMemory`.
2. Scans all players and asserts player index 0 is Tyrese Maxey.
3. Resolves the `career_stats` pointer to locate the season statistics table.
4. For each of 5 season slots (24-25, 23-24, 22-23, 21-22, 20-21):
   - Reads all stat fields (pts, reb, ast, stl, blk, FGM, FGA, 3PM, 3PA, FTM, FTA, min, oreb, TO, fouls, GS, GP, DD, TD, +/-).
   - Asserts each value matches a hardcoded reference table from game screenshots.

**Reference data:** `_EXPECTED_TOTALS_BY_SLOT` (5 entries × 20 fields).

**Why it matters for memory work:** This is the highest-fidelity test of the
full decode pipeline — process attachment, pointer chain traversal, multi-slot
stats table navigation, and field conversion. If any step of the memory layer
is broken, this test will catch it precisely. Run it after any changes to
`GameMemory`, `PlayerDataModel`, `core/offsets.py`, or
`core/conversions.py`.

---

## Performance Thresholds

All performance tests respect environment variable overrides:

| Env var | Default | Governs |
|---|---|---|
| `NBA2K_EDITOR_PERF_STARTUP_MAX` | `5.0` s | `test_perf_startup.py` |
| `NBA2K_EDITOR_PERF_DATA_MODEL_MAX` | `5.0` s | `test_perf_data_model.py` |
| `NBA2K_EDITOR_PERF_IMPORT_MAX` | `8.0` s | `test_perf_import.py` |

Set `NBA2K_EDITOR_PROFILE=1` to enable `@timed` instrumentation so the `summarize()` assertions have data.

---

## Known Issues / Outstanding Gaps

| # | File | Issue |
|---|---|---|
| 1 | `nba2k26_editor/ui/extensions_ui.py` | `_key_to_module_name` converts `nba2k26_editor.` → `nba2k_editor.` for backwards compat with old extension config files. Since `nba2k_editor` no longer exists, extensions stored under the old key will fail to import. Needs a migration path. |
| 2 | `test_startup_import_hygiene.py` | The `torch` check is now trivially true (AI/RL modules removed). The test is still useful for `pandas` hygiene. |
| 3 | No tests for `memory/game_memory.py` | `GameMemory` has no unit tests because it calls Win32 APIs directly. Priority candidate for abstraction behind a protocol interface (see architecture review item #4) after which it can be properly mocked. |
| 4 | No tests for `memory/scan_utils.py` | Pattern scanner is used by `GameMemory` but has no dedicated tests. |
| 5 | No tests for `core/dynamic_bases.py` | ASLR base detection logic is untested in isolation. |
| 6 | No tests for `core/conversions.py` | The bijective converters (height, weight, badge levels, potentials) have no unit tests — highest-priority gap once memory integration testing begins. |
