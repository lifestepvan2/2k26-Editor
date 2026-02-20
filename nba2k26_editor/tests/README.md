# tests folder

## Responsibilities
- Regression/perf/integration suites across editor subsystems.
- Owns direct Python files: `generate_call_graph.py`, `test_action_legality.py`, `test_app_full_editor_child_launch.py`, `test_async_exception_callbacks.py`, `test_cba_action_legality.py`, `test_cba_assistant_context.py`, `test_cba_extraction.py`, `test_data_model_category_grouping.py`, `test_dead_code_proof_tool.py`, `test_editor_live_adapter.py`, `test_excel_callbacks_regression.py`, `test_features.py`, `test_full_editor_entrypoint.py`, `test_full_editor_launch.py`, `test_full_editor_selective_save.py`, `test_full_player_editor_int_bounds.py`, `test_full_player_editor_stats_slots.py`, `test_gm_rl_integration.py`, `test_io_codec_services.py`, `test_launch_editor_child_mode.py`, `test_league_history_probe_validation.py`, `test_live_tyrese_maxey_stats_alignment.py`, `test_offsets_services.py`, `test_perf_data_model.py`, `test_perf_import.py`, `test_perf_startup.py`, `test_ppo_math.py`, `test_rollout_buffer.py`, `test_runtime_smoke.py`, `test_scan_entrypoint_compat.py`, `test_split_offsets_fidelity.py`, `test_startup_import_hygiene.py`, `test_startup_load_order.py`, `test_stats_tab_routing.py`, `test_strict_offset_mapping.py`, `test_team_pointer_field_behavior.py`, `test_trade_state.py`, `test_ui_screen_loading_regression.py`.
- Maintains folder-local runtime behavior and boundaries used by the editor.

## Technical Deep Dive
Regression/perf/integration suites across editor subsystems.
This folder currently has 38 direct Python modules. Function-tree coverage below is exhaustive for direct files and includes nested callables.

## Runtime/Data Flow
1. Callers enter this folder through public entry modules or imported helper functions.
2. Folder code performs domain-specific orchestration and delegates to adjacent layers as needed.
3. Results/events/state are returned to UI, model, runtime, or CLI callers depending on workflow.

## Integration Points
- Integrated within `nba2k_editor/tests` runtime graph.
- Consumed by neighboring package layers through imports and method calls.

## Function Tree
### `generate_call_graph.py`
- [def] generate_call_graph.py::_module_name_for
- [def] generate_call_graph.py::_resolve_from_module
- [def] generate_call_graph.py::_expr_text
- [def] generate_call_graph.py::_flatten_attr
- [def] generate_call_graph.py::collect_modules
- [def] generate_call_graph.py::parse_modules
- [def] generate_call_graph.py::collect_defs
- [def] generate_call_graph.py::collect_imports
- [def] generate_call_graph.py::build_symbol_indexes
- [def] generate_call_graph.py::resolve_symbol_target
- [def] generate_call_graph.py::resolve_expr_targets
- [def] generate_call_graph.py::walk_calls
- [def] generate_call_graph.py::build_edges
  - [def] generate_call_graph.py::build_edges.add_edge
- [def] generate_call_graph.py::write_outputs
- [def] generate_call_graph.py::main

### `test_action_legality.py`
- [def] test_action_legality.py::test_draft_mask_blocks_full_roster
- [def] test_action_legality.py::test_roster_move_mask_respects_minimum

### `test_app_full_editor_child_launch.py`
  - [def] test_app_full_editor_child_launch.py::_MemStub.__init__
  - [def] test_app_full_editor_child_launch.py::_MemStub.open_process
  - [def] test_app_full_editor_child_launch.py::_ModelStub.__init__
  - [def] test_app_full_editor_child_launch.py::_ModelStub.refresh_players
  - [def] test_app_full_editor_child_launch.py::_ModelStub.get_teams
  - [def] test_app_full_editor_child_launch.py::_ModelStub._team_index_for_display_name
  - [def] test_app_full_editor_child_launch.py::_ModelStub.get_staff
  - [def] test_app_full_editor_child_launch.py::_ModelStub.get_stadiums
- [def] test_app_full_editor_child_launch.py::test_open_full_editor_launches_child_with_player_indices
- [def] test_app_full_editor_child_launch.py::test_open_full_team_editor_launches_child_with_resolved_team_index
- [def] test_app_full_editor_child_launch.py::test_open_full_staff_editor_launches_selected_scanned_index
- [def] test_app_full_editor_child_launch.py::test_selected_staff_indices_return_scanned_id_not_filtered_position
- [def] test_app_full_editor_child_launch.py::test_selected_stadium_indices_return_scanned_id_not_filtered_position

### `test_async_exception_callbacks.py`
  - [def] test_async_exception_callbacks.py::_CallbackAppStub.__init__
  - [def] test_async_exception_callbacks.py::_CallbackAppStub.run_on_ui_thread
  - [def] test_async_exception_callbacks.py::_AssistantPanelStub.__init__
  - [def] test_async_exception_callbacks.py::_AssistantPanelStub._finalize_request
  - [def] test_async_exception_callbacks.py::_AssistantPanelStub._append_output
  - [def] test_async_exception_callbacks.py::_DynamicScanStub.__init__
  - [def] test_async_exception_callbacks.py::_DynamicScanStub._hook_label_for
  - [def] test_async_exception_callbacks.py::_DynamicScanStub._set_dynamic_scan_status
  - [def] test_async_exception_callbacks.py::_DynamicScanStub.run_on_ui_thread
  - [def] test_async_exception_callbacks.py::_DynamicScanStub.show_error
  - [def] test_async_exception_callbacks.py::_DynamicScanStub.show_warning
  - [def] test_async_exception_callbacks.py::_DynamicScanStub.show_info
  - [def] test_async_exception_callbacks.py::_DynamicScanStub._update_status
  - [def] test_async_exception_callbacks.py::_DynamicScanStub._start_scan
- [def] test_async_exception_callbacks.py::_run_ui_callbacks
- [def] test_async_exception_callbacks.py::test_ai_panel_deferred_error_callback_preserves_exception_message
  - [def] test_async_exception_callbacks.py::test_ai_panel_deferred_error_callback_preserves_exception_message._raise_backend
- [def] test_async_exception_callbacks.py::test_dynamic_scan_offsets_load_error_callback_survives_exception_scope
  - [def] test_async_exception_callbacks.py::test_dynamic_scan_offsets_load_error_callback_survives_exception_scope._raise_offsets
- [def] test_async_exception_callbacks.py::test_dynamic_scan_failure_warning_callback_survives_exception_scope
  - [def] test_async_exception_callbacks.py::test_dynamic_scan_failure_warning_callback_survives_exception_scope._raise_scan
- [def] test_async_exception_callbacks.py::test_dynamic_apply_failure_warning_callback_survives_exception_scope
  - [def] test_async_exception_callbacks.py::test_dynamic_apply_failure_warning_callback_survives_exception_scope._init_offsets

### `test_cba_action_legality.py`
- [def] test_cba_action_legality.py::_ruleset
- [def] test_cba_action_legality.py::test_cba_blocks_trade_after_deadline_and_emits_warning
- [def] test_cba_action_legality.py::test_cba_blocks_contracts_when_hard_cap_reached

### `test_cba_assistant_context.py`
- [def] test_cba_assistant_context.py::test_cba_guidance_contains_core_constraints

### `test_cba_extraction.py`
- [def] test_cba_extraction.py::_source_doc
- [def] test_cba_extraction.py::test_cba_extraction_core_constants_and_tables

### `test_data_model_category_grouping.py`
- [def] test_data_model_category_grouping.py::test_get_categories_for_super_groups_player_categories

### `test_dead_code_proof_tool.py`
- [def] test_dead_code_proof_tool.py::test_find_symbol_refs_excludes_comments_strings_and_substrings
- [def] test_dead_code_proof_tool.py::test_callback_ref_edges_are_captured
- [def] test_dead_code_proof_tool.py::test_classification_rules
- [def] test_dead_code_proof_tool.py::test_runtime_instrumentation_preserves_binding_and_exception
    - [def] test_dead_code_proof_tool.py::test_runtime_instrumentation_preserves_binding_and_exception.Demo.__init__
    - [def] test_dead_code_proof_tool.py::test_runtime_instrumentation_preserves_binding_and_exception.Demo.add
    - [def] test_dead_code_proof_tool.py::test_runtime_instrumentation_preserves_binding_and_exception.Demo.boom

### `test_editor_live_adapter.py`
  - [def] test_editor_live_adapter.py::_StubMem.__init__
  - [def] test_editor_live_adapter.py::_StubMem.open_process
  - [def] test_editor_live_adapter.py::_StubModel.__init__
  - [def] test_editor_live_adapter.py::_StubModel.refresh_players
  - [def] test_editor_live_adapter.py::_StubModel._build_team_list_from_players
- [def] test_editor_live_adapter.py::test_live_adapter_builds_roster_from_stub
- [def] test_editor_live_adapter.py::test_rotation_minutes_cap_enforced
- [def] test_editor_live_adapter.py::test_trade_swaps_rosters

### `test_excel_callbacks_regression.py`
  - [def] test_excel_callbacks_regression.py::_ContextStub.__enter__
  - [def] test_excel_callbacks_regression.py::_ContextStub.__exit__
  - [def] test_excel_callbacks_regression.py::_ExcelScreenAppStub.__init__
  - [def] test_excel_callbacks_regression.py::_ExcelScreenAppStub._import_excel
  - [def] test_excel_callbacks_regression.py::_ExcelScreenAppStub._export_excel
  - [def] test_excel_callbacks_regression.py::_ExcelAppStub.__init__
  - [def] test_excel_callbacks_regression.py::_ExcelAppStub.show_error
  - [def] test_excel_callbacks_regression.py::_ExcelAppStub.show_info
  - [def] test_excel_callbacks_regression.py::_VarStub.__init__
  - [def] test_excel_callbacks_regression.py::_VarStub.set
  - [def] test_excel_callbacks_regression.py::_VarStub.get
  - [def] test_excel_callbacks_regression.py::_ExportFinishAppStub.__init__
  - [def] test_excel_callbacks_regression.py::_ExportFinishAppStub._reset_excel_progress
  - [def] test_excel_callbacks_regression.py::_ExportFinishAppStub._set_excel_status
  - [def] test_excel_callbacks_regression.py::_ExportFinishAppStub.show_info
  - [def] test_excel_callbacks_regression.py::_ExportFinishAppStub.show_error
- [def] test_excel_callbacks_regression.py::test_excel_section_callbacks_ignore_user_data
  - [def] test_excel_callbacks_regression.py::test_excel_section_callbacks_ignore_user_data._fake_add_button
- [def] test_excel_callbacks_regression.py::test_import_excel_blank_entity_reports_error
- [def] test_excel_callbacks_regression.py::test_export_excel_blank_entity_reports_error
- [def] test_excel_callbacks_regression.py::test_open_file_dialog_uses_add_file_extension_filters
  - [def] test_excel_callbacks_regression.py::test_open_file_dialog_uses_add_file_extension_filters._fake_add_file_dialog
  - [def] test_excel_callbacks_regression.py::test_open_file_dialog_uses_add_file_extension_filters._fake_add_file_extension
- [def] test_excel_callbacks_regression.py::test_finish_excel_export_success_keeps_completion_visible
    - [def] test_excel_callbacks_regression.py::test_finish_excel_export_success_keeps_completion_visible._Result.summary_text

### `test_features.py`
- [def] test_features.py::test_feature_shapes_and_masks
- [def] test_features.py::test_nan_imputation_and_masks

### `test_full_editor_entrypoint.py`
  - [def] test_full_editor_entrypoint.py::_MemStub.__init__
  - [def] test_full_editor_entrypoint.py::_MemStub.open_process
  - [def] test_full_editor_entrypoint.py::_ModelStub.__init__
  - [def] test_full_editor_entrypoint.py::_ModelStub.refresh_players
- [def] test_full_editor_entrypoint.py::test_parse_editor_request_player_indices
- [def] test_full_editor_entrypoint.py::test_parse_editor_request_requires_index_for_team
- [def] test_full_editor_entrypoint.py::test_open_requested_editor_routes_player
  - [def] test_full_editor_entrypoint.py::test_open_requested_editor_routes_player._fake_player_editor
- [def] test_full_editor_entrypoint.py::test_open_requested_editor_routes_team
  - [def] test_full_editor_entrypoint.py::test_open_requested_editor_routes_team._fake_team_editor

### `test_full_editor_launch.py`
- [def] test_full_editor_launch.py::test_build_launch_command_source_mode
- [def] test_full_editor_launch.py::test_build_launch_command_frozen_mode
- [def] test_full_editor_launch.py::test_build_launch_command_player_indices_deduplicated

### `test_full_editor_selective_save.py`
  - [def] test_full_editor_selective_save.py::_DPGStub.__init__
  - [def] test_full_editor_selective_save.py::_DPGStub.does_item_exist
  - [def] test_full_editor_selective_save.py::_DPGStub.get_value
  - [def] test_full_editor_selective_save.py::_DPGStub.set_value
  - [def] test_full_editor_selective_save.py::_AppStub.__init__
  - [def] test_full_editor_selective_save.py::_AppStub.show_message
  - [def] test_full_editor_selective_save.py::_AppStub.show_error
  - [def] test_full_editor_selective_save.py::_ModelStub.__init__
  - [def] test_full_editor_selective_save.py::_ModelStub.encode_field_value
- [def] test_full_editor_selective_save.py::test_full_player_editor_saves_only_changed_fields
- [def] test_full_editor_selective_save.py::test_full_player_editor_does_not_save_fields_without_baseline
- [def] test_full_editor_selective_save.py::test_full_player_editor_multi_target_writes_changed_fields_for_all_targets
- [def] test_full_editor_selective_save.py::test_full_team_editor_saves_only_changed_fields

### `test_full_player_editor_int_bounds.py`
- [def] test_full_player_editor_int_bounds.py::test_sanitize_input_int_range_clamps_to_dpg_int_bounds
- [def] test_full_player_editor_int_bounds.py::test_add_field_control_caps_large_integer_bit_length
  - [def] test_full_player_editor_int_bounds.py::test_add_field_control_caps_large_integer_bit_length._fake_add_input_int

### `test_full_player_editor_stats_slots.py`
- [def] test_full_player_editor_stats_slots.py::test_prepare_stats_tabs_keeps_career_and_season_awards_merge
- [def] test_full_player_editor_stats_slots.py::test_prepare_stats_tabs_adds_season_slot_selector_and_hides_stats_ids

### `test_gm_rl_integration.py`
- [def] test_gm_rl_integration.py::test_gm_rl_alias_points_to_integrated_package

### `test_io_codec_services.py`
  - [def] test_io_codec_services.py::_StubModel.__init__
  - [def] test_io_codec_services.py::_StubModel.mark_dirty
  - [def] test_io_codec_services.py::_StubModel.get_field_value_typed
  - [def] test_io_codec_services.py::_StubModel.set_field_value_typed
  - [def] test_io_codec_services.py::_StubModel.get_team_field_value_typed
  - [def] test_io_codec_services.py::_StubModel.set_team_field_value_typed
  - [def] test_io_codec_services.py::_StubModel.get_team_fields
  - [def] test_io_codec_services.py::_StubModel.set_team_fields
  - [def] test_io_codec_services.py::_StubModel.refresh_players
- [def] test_io_codec_services.py::test_io_codec_routes_player_and_team_calls
- [def] test_io_codec_services.py::test_services_mark_dirty_on_writes

### `test_launch_editor_child_mode.py`
- [def] test_launch_editor_child_mode.py::test_run_child_full_editor_if_requested_routes_arguments
- [def] test_launch_editor_child_mode.py::test_run_child_full_editor_if_requested_returns_false_without_flag

### `test_league_history_probe_validation.py`
- [def] test_league_history_probe_validation.py::test_get_league_records_accepts_base_when_first_row_is_blank_but_next_row_has_data
    - [def] test_league_history_probe_validation.py::test_get_league_records_accepts_base_when_first_row_is_blank_but_next_row_has_data._MemStub.__init__
    - [def] test_league_history_probe_validation.py::test_get_league_records_accepts_base_when_first_row_is_blank_but_next_row_has_data._MemStub.open_process
    - [def] test_league_history_probe_validation.py::test_get_league_records_accepts_base_when_first_row_is_blank_but_next_row_has_data._MemStub.read_bytes
  - [def] test_league_history_probe_validation.py::test_get_league_records_accepts_base_when_first_row_is_blank_but_next_row_has_data._resolve_league_base
  - [def] test_league_history_probe_validation.py::test_get_league_records_accepts_base_when_first_row_is_blank_but_next_row_has_data._decode_field_value_from_buffer

### `test_live_tyrese_maxey_stats_alignment.py`
- [def] test_live_tyrese_maxey_stats_alignment.py::_verify_enabled
- [def] test_live_tyrese_maxey_stats_alignment.py::_field_by_name
- [def] test_live_tyrese_maxey_stats_alignment.py::_season_record_ptr
- [def] test_live_tyrese_maxey_stats_alignment.py::_to_int
- [def] test_live_tyrese_maxey_stats_alignment.py::_field_metadata
- [def] test_live_tyrese_maxey_stats_alignment.py::_load_live_tyrese_context
- [def] test_live_tyrese_maxey_stats_alignment.py::test_live_tyrese_maxey_player0_stats_match_reference_table
- [def] test_live_tyrese_maxey_stats_alignment.py::test_live_tyrese_maxey_full_editor_season_slot_load_matches_reference_table
    - [def] test_live_tyrese_maxey_stats_alignment.py::test_live_tyrese_maxey_full_editor_season_slot_load_matches_reference_table._DPGStub.__init__
    - [def] test_live_tyrese_maxey_stats_alignment.py::test_live_tyrese_maxey_full_editor_season_slot_load_matches_reference_table._DPGStub.does_item_exist
    - [def] test_live_tyrese_maxey_stats_alignment.py::test_live_tyrese_maxey_full_editor_season_slot_load_matches_reference_table._DPGStub.get_value
    - [def] test_live_tyrese_maxey_stats_alignment.py::test_live_tyrese_maxey_full_editor_season_slot_load_matches_reference_table._DPGStub.set_value

### `test_offsets_services.py`
- [def] test_offsets_services.py::test_offset_cache_target_roundtrip
- [def] test_offsets_services.py::test_offset_resolver_prefers_converted_payload
- [def] test_offsets_services.py::test_offset_resolver_require_dict_raises
- [def] test_offsets_services.py::test_offset_repository_loads_and_caches
- [def] test_offsets_services.py::test_initialize_offsets_applies_explicit_filename_even_when_target_cached
  - [def] test_offsets_services.py::test_initialize_offsets_applies_explicit_filename_even_when_target_cached._fake_apply_offset_config

### `test_perf_data_model.py`
  - [def] test_perf_data_model.py::_StubMem.__init__
  - [def] test_perf_data_model.py::_StubMem.open_process
- [def] test_perf_data_model.py::test_data_model_refresh_perf_harness
- [def] test_perf_data_model.py::test_data_model_init_reuses_loaded_offsets_for_same_target
  - [def] test_perf_data_model.py::test_data_model_init_reuses_loaded_offsets_for_same_target._fake_initialize_offsets

### `test_perf_import.py`
  - [def] test_perf_import.py::_StubModel.__init__
  - [def] test_perf_import.py::_StubModel.get_categories_for_super
  - [def] test_perf_import.py::_StubModel.encode_field_value
  - [def] test_perf_import.py::_StubModel.decode_field_value
- [def] test_perf_import.py::_build_workbook
- [def] test_perf_import.py::test_import_export_perf_harness

### `test_perf_startup.py`
  - [def] test_perf_startup.py::_StubMem.__init__
  - [def] test_perf_startup.py::_StubMem.open_process
  - [def] test_perf_startup.py::_StubModel.__init__
  - [def] test_perf_startup.py::_StubApp.__init__
- [def] test_perf_startup.py::test_gui_startup_perf_harness
- [def] test_perf_startup.py::test_gui_startup_does_not_reinitialize_offsets_in_model
  - [def] test_perf_startup.py::test_gui_startup_does_not_reinitialize_offsets_in_model._fake_initialize_offsets

### `test_ppo_math.py`
- [def] test_ppo_math.py::_dummy_obs
- [def] test_ppo_math.py::_dummy_mask
- [def] test_ppo_math.py::test_gae_shapes_and_last_step

### `test_rollout_buffer.py`
- [def] test_rollout_buffer.py::make_mask
- [def] test_rollout_buffer.py::test_rollout_buffer_ordering_and_dones

### `test_runtime_smoke.py`
- [def] test_runtime_smoke.py::test_runtime_mask_from_info_smoke
- [def] test_runtime_smoke.py::test_ppo_mask_stack_smoke

### `test_scan_entrypoint_compat.py`
  - [def] test_scan_entrypoint_compat.py::_ScanModelStub.__init__
  - [def] test_scan_entrypoint_compat.py::_ScanModelStub.refresh_players
  - [def] test_scan_entrypoint_compat.py::_ScanModelStub.get_teams
  - [def] test_scan_entrypoint_compat.py::_ScanAppStub.__init__
  - [def] test_scan_entrypoint_compat.py::_ScanAppStub._update_team_dropdown
  - [def] test_scan_entrypoint_compat.py::_ScanAppStub._refresh_player_list
  - [def] test_scan_entrypoint_compat.py::_ScanAppStub._on_team_edit_selected
  - [def] test_scan_entrypoint_compat.py::_ScanAppStub._render_player_list
- [def] test_scan_entrypoint_compat.py::test_start_scan_wrapper_uses_shared_flow_without_regression
- [def] test_scan_entrypoint_compat.py::test_start_team_scan_wrapper_preserves_pending_selection_behavior
- [def] test_scan_entrypoint_compat.py::test_scan_thread_wrapper_handles_refresh_failure_without_stalling
- [def] test_scan_entrypoint_compat.py::test_scan_teams_thread_wrapper_handles_refresh_failure_without_stalling

### `test_split_offsets_fidelity.py`
- [def] test_split_offsets_fidelity.py::_load_2k26_config
- [def] test_split_offsets_fidelity.py::_offset_entries
- [def] test_split_offsets_fidelity.py::test_stats_table_categories_are_emitted_without_flat_stats_alias
- [def] test_split_offsets_fidelity.py::test_player_stats_relations_link_ids_to_season_only
- [def] test_split_offsets_fidelity.py::test_parse_report_accounts_for_all_discovered_leaf_fields
- [def] test_split_offsets_fidelity.py::test_type_normalization_covers_observed_player_types
- [def] test_split_offsets_fidelity.py::test_split_entries_include_traceability_and_inference_metadata
- [def] test_split_offsets_fidelity.py::test_version_metadata_preserves_non_core_selected_version_keys

### `test_startup_import_hygiene.py`
- [def] test_startup_import_hygiene.py::test_ui_app_import_does_not_eager_load_heavy_agent_dependencies

### `test_startup_load_order.py`
  - [def] test_startup_load_order.py::_StubMem.__init__
  - [def] test_startup_load_order.py::_StubMem.open_process
  - [def] test_startup_load_order.py::_AppModelStub.__init__
  - [def] test_startup_load_order.py::_AppModelStub.get_teams
- [def] test_startup_load_order.py::test_model_init_does_not_reinitialize_offsets_for_loaded_target
  - [def] test_startup_load_order.py::test_model_init_does_not_reinitialize_offsets_for_loaded_target._fake_initialize_offsets
- [def] test_startup_load_order.py::test_show_ai_builds_screen_and_starts_bridge_lazily
  - [def] test_startup_load_order.py::test_show_ai_builds_screen_and_starts_bridge_lazily._fake_build_ai
  - [def] test_startup_load_order.py::test_show_ai_builds_screen_and_starts_bridge_lazily._fake_start_bridge
- [def] test_startup_load_order.py::test_show_agent_starts_polling_only_after_screen_is_opened
  - [def] test_startup_load_order.py::test_show_agent_starts_polling_only_after_screen_is_opened._fake_build_agent
  - [def] test_startup_load_order.py::test_show_agent_starts_polling_only_after_screen_is_opened._fake_start_polling

### `test_stats_tab_routing.py`
- [def] test_stats_tab_routing.py::test_prepare_stats_tabs_duplicates_awards_into_career_and_season
- [def] test_stats_tab_routing.py::test_prepare_stats_tabs_replaces_stats_ids_with_season_slot_dropdown
- [def] test_stats_tab_routing.py::test_league_pointer_for_career_category_uses_career_stats_pointer
  - [def] test_stats_tab_routing.py::test_league_pointer_for_career_category_uses_career_stats_pointer._fake_pointer_meta
- [def] test_stats_tab_routing.py::test_league_pointer_for_season_category_uses_nba_history_pointer
  - [def] test_stats_tab_routing.py::test_league_pointer_for_season_category_uses_nba_history_pointer._fake_pointer_meta

### `test_strict_offset_mapping.py`
- [def] test_strict_offset_mapping.py::restore_offsets_state
- [def] test_strict_offset_mapping.py::_entry
- [def] test_strict_offset_mapping.py::_strict_offsets_payload
- [def] test_strict_offset_mapping.py::_new_league_model_stub
- [def] test_strict_offset_mapping.py::test_apply_offset_config_accepts_exact_mapping_for_all_base_pointer_keys
- [def] test_strict_offset_mapping.py::test_apply_offset_config_rejects_case_variant_base_pointer_key
- [def] test_strict_offset_mapping.py::test_apply_offset_config_rejects_case_variant_size_key
- [def] test_strict_offset_mapping.py::test_apply_offset_config_fails_when_required_size_missing
- [def] test_strict_offset_mapping.py::test_apply_offset_config_does_not_fallback_to_team_stadium_for_stadium_name
- [def] test_strict_offset_mapping.py::test_league_pointer_meta_ignores_case_variant_pointer_keys
- [def] test_strict_offset_mapping.py::test_league_stride_requires_exact_mapped_size_key
- [def] test_strict_offset_mapping.py::test_resolve_version_context_prefers_top_level_base_pointers_and_version_game_info
- [def] test_strict_offset_mapping.py::test_resolve_version_context_falls_back_to_version_base_pointers_when_top_level_missing
- [def] test_strict_offset_mapping.py::test_league_context_delegates_to_offsets_resolver
  - [def] test_strict_offset_mapping.py::test_league_context_delegates_to_offsets_resolver._fake_resolve
- [def] test_strict_offset_mapping.py::test_league_pointer_meta_does_not_build_fallback_chain_when_parser_returns_empty
- [def] test_strict_offset_mapping.py::test_league_pointer_meta_uses_canonical_parser_output

### `test_team_pointer_field_behavior.py`
- [def] test_team_pointer_field_behavior.py::test_decode_team_pointer_field_displays_team_name
- [def] test_team_pointer_field_behavior.py::test_decode_non_team_pointer_field_stays_hex
- [def] test_team_pointer_field_behavior.py::test_encode_team_pointer_field_accepts_team_name
  - [def] test_team_pointer_field_behavior.py::test_encode_team_pointer_field_accepts_team_name._capture_write

### `test_trade_state.py`
- [def] test_trade_state.py::test_trade_state_add_and_package_projection
- [def] test_trade_state.py::test_trade_state_prevents_duplicates_and_remove
- [def] test_trade_state.py::test_trade_state_clear_slot

### `test_ui_screen_loading_regression.py`
  - [def] test_ui_screen_loading_regression.py::_ScanModelStub.__init__
  - [def] test_ui_screen_loading_regression.py::_ScanModelStub.refresh_players
  - [def] test_ui_screen_loading_regression.py::_ScanModelStub.get_teams
  - [def] test_ui_screen_loading_regression.py::_ScanAppStub.__init__
  - [def] test_ui_screen_loading_regression.py::_ScanAppStub.run_on_ui_thread
  - [def] test_ui_screen_loading_regression.py::_ScanAppStub._update_team_dropdown
  - [def] test_ui_screen_loading_regression.py::_ScanAppStub._refresh_player_list
  - [def] test_ui_screen_loading_regression.py::_ScanAppStub._on_team_edit_selected
  - [def] test_ui_screen_loading_regression.py::_ScanAppStub._render_player_list
  - [def] test_ui_screen_loading_regression.py::_TradeModelStub.__init__
  - [def] test_ui_screen_loading_regression.py::_TradeModelStub.refresh_players
  - [def] test_ui_screen_loading_regression.py::_TradeAppStub.__init__
  - [def] test_ui_screen_loading_regression.py::_TradeAppStub._trade_ensure_slot_entries
  - [def] test_ui_screen_loading_regression.py::_TradeAppStub._trade_render_team_lists
  - [def] test_ui_screen_loading_regression.py::_AppModelStub.__init__
  - [def] test_ui_screen_loading_regression.py::_AppModelStub.get_teams
  - [def] test_ui_screen_loading_regression.py::_LegacyLeagueCategoryModelStub.get_categories_for_super
- [def] test_ui_screen_loading_regression.py::test_scan_thread_updates_ui_on_success
- [def] test_ui_screen_loading_regression.py::test_scan_thread_handles_refresh_failure_without_stalling
- [def] test_ui_screen_loading_regression.py::test_scan_teams_thread_handles_refresh_failure_without_stalling
- [def] test_ui_screen_loading_regression.py::test_trade_refresh_team_options_bootstraps_from_refresh
- [def] test_ui_screen_loading_regression.py::test_show_ai_builds_screen_and_bridge_lazily
  - [def] test_ui_screen_loading_regression.py::test_show_ai_builds_screen_and_bridge_lazily._fake_build_ai
  - [def] test_ui_screen_loading_regression.py::test_show_ai_builds_screen_and_bridge_lazily._fake_start_bridge
- [def] test_ui_screen_loading_regression.py::test_show_agent_builds_screen_and_starts_polling_lazily
  - [def] test_ui_screen_loading_regression.py::test_show_agent_builds_screen_and_starts_polling_lazily._fake_build_agent
  - [def] test_ui_screen_loading_regression.py::test_show_agent_builds_screen_and_starts_polling_lazily._fake_start_polling
- [def] test_ui_screen_loading_regression.py::test_show_nba_history_routes_to_history_page_and_refreshes
- [def] test_ui_screen_loading_regression.py::test_show_nba_records_routes_to_records_page_and_refreshes
- [def] test_ui_screen_loading_regression.py::test_show_league_alias_routes_to_nba_history_page
- [def] test_ui_screen_loading_regression.py::test_ensure_league_categories_splits_legacy_league_supertype
- [def] test_ui_screen_loading_regression.py::test_start_scan_uses_shared_scan_flow
- [def] test_ui_screen_loading_regression.py::test_start_team_scan_applies_pending_selection_via_shared_flow

## Failure Modes and Debugging
- Upstream schema or dependency drift can surface runtime failures in this layer.
- Environment mismatches (platform, optional deps, file paths) can reduce or disable functionality.
- Nested call paths are easiest to diagnose by following this README function tree and runtime logs.

## Test Coverage Notes
- This folder itself is the executable test suite; run with `python -m pytest -q`.
- Individual suites can be run by file path for targeted validation.
