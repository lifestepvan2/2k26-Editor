# Call Graph (Static)

Generated from AST analysis. This captures static call/callback references in `nba2k_editor`.

## Summary
- Modules: 128
- Nodes (functions + module scopes): 1380
- Call edges: 2854
- Callback-reference edges: 144

## Artifacts
- Machine-readable graph: `call_graph.json`
- This index: `CALL_GRAPH.md`

## Limitations
- Dynamic dispatch (`getattr`, reflective calls), runtime monkey-patching, and library-internal callbacks may not resolve.
- Import aliasing and chained attributes are resolved best-effort for in-repo modules only.
- This graph is static and does not represent runtime execution frequency or conditional reachability.

## How To Trace
1. Locate a node id in `call_graph.json` (format: `module::qualname`).
2. Check its `calls`, `called_by`, and `callback_refs` arrays.
3. Use `edges` for line-level detail and edge kind.

## Top Fan-Out Nodes
- `nba2k_editor.core.offsets::<module>` -> 32 calls
- `nba2k_editor.ui.app::<module>` -> 32 calls
- `nba2k_editor.importing.excel_import::<module>` -> 29 calls
- `nba2k_editor.models.data_model::PlayerDataModel.decode_field_value` -> 23 calls
- `nba2k_editor.logs.logging::<module>` -> 20 calls
- `nba2k_editor.models.data_model::PlayerDataModel.decode_field_value_from_buffer` -> 19 calls
- `nba2k_editor.models.data_model::PlayerDataModel._coerce_field_value` -> 18 calls
- `nba2k_editor.models.data_model::<module>` -> 17 calls
- `nba2k_editor.gm_rl.cba.extractors::<module>` -> 16 calls
- `nba2k_editor.core.dynamic_bases::<module>` -> 13 calls
- `nba2k_editor.ui.app::PlayerEditorApp.build_ui` -> 13 calls
- `nba2k_editor.entrypoints.gui::<module>` -> 12 calls
- `nba2k_editor.ui.extensions_ui::<module>` -> 12 calls
- `nba2k_editor.ai.assistant::<module>` -> 11 calls
- `nba2k_editor.ai.nba_data::<module>` -> 10 calls
- `nba2k_editor.importing.excel_import::import_excel_workbook` -> 10 calls
- `nba2k_editor.ui.app::PlayerEditorApp._export_excel` -> 10 calls
- `nba2k_editor.core.offsets::_load_categories` -> 9 calls
- `nba2k_editor.entrypoints.gui::main` -> 9 calls
- `nba2k_editor.gm_rl.cba.extractors::extract_raw_rules` -> 9 calls
- `nba2k_editor.importing.excel_import::export_excel_workbook` -> 9 calls
- `nba2k_editor.models.data_model::PlayerDataModel.refresh_players` -> 9 calls
- `nba2k_editor.ui.app::PlayerEditorApp._import_excel` -> 9 calls
- `nba2k_editor.core.offsets::_apply_offset_config` -> 8 calls
- `nba2k_editor.entrypoints.extract_cba_rules::<module>` -> 8 calls

## Top Fan-In Nodes
- `nba2k_editor.core.conversions::to_int` <- 53 callers
- `nba2k_editor.ai.assistant::LLMControlBridge._run_on_ui_thread` <- 38 callers
- `nba2k_editor.ui.app::PlayerEditorApp.show_error` <- 19 callers
- `nba2k_editor.ui.app::PlayerEditorApp.show_info` <- 17 callers
- `nba2k_editor.ai.assistant::LLMControlBridge._get_control_value` <- 15 callers
- `nba2k_editor.core.perf::timed` <- 15 callers
- `nba2k_editor.models.data_model::PlayerDataModel._read_string` <- 14 callers
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_team_base_ptr` <- 11 callers
- `nba2k_editor.ui.app::PlayerEditorApp._show_screen` <- 11 callers
- `nba2k_editor.models.data_model::PlayerDataModel._effective_byte_length` <- 10 callers
- `nba2k_editor.ui.app::PlayerEditorApp._reset_excel_progress` <- 10 callers
- `nba2k_editor.ai.assistant::LLMControlBridge._select_player_index` <- 9 callers
- `nba2k_editor.ai.assistant::LLMControlBridge._find_open_staff_editor` <- 9 callers
- `nba2k_editor.ai.assistant::LLMControlBridge._find_open_stadium_editor` <- 9 callers
- `nba2k_editor.models.data_model::PlayerDataModel._player_record_address` <- 9 callers
- `nba2k_editor.models.data_model::PlayerDataModel._normalize_field_type` <- 9 callers
- `nba2k_editor.core.offsets::initialize_offsets` <- 8 callers
- `nba2k_editor.models.services.io_codec::IOCodec.__init__` <- 8 callers
- `nba2k_editor.ui.app::PlayerEditorApp._open_file_dialog` <- 8 callers
- `nba2k_editor.ui.app::PlayerEditorApp._trade_update_status` <- 8 callers
- `nba2k_editor.ai.assistant::LLMControlBridge._find_open_full_editor` <- 7 callers
- `nba2k_editor.ai.backends.python_backend::load_instance` <- 7 callers
- `nba2k_editor.ai.backends.python_backend::generate_sync` <- 7 callers
- `nba2k_editor.core.conversions::raw_height_to_inches` <- 7 callers
- `nba2k_editor.gm_rl.cba.extractors::_add_citation` <- 7 callers

## Module Index
### `nba2k_editor.__init__`
- `nba2k_editor.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.__main__`
- `nba2k_editor.__main__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ai.__init__`
- `nba2k_editor.ai.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ai.assistant`
- `nba2k_editor.ai.assistant::<module>` | calls=11 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.__init__` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.app` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._start_server` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._start_server.handler_factory` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.ControlHandler._start_server.handler_factory._send_json` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.ControlHandler._start_server.handler_factory.do_OPTIONS` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.ControlHandler._start_server.handler_factory.do_GET` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.ControlHandler._start_server.handler_factory.do_POST` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.ControlHandler._start_server.handler_factory.log_message` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.describe_state` | calls=3 called_by=1 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge.describe_state.gather` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.list_players` | calls=1 called_by=1 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge.list_players.gather` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.handle_command` | calls=6 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.feature_actions` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.available_actions` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_select_player` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_select_staff` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_select_stadium` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._select_player_index` | calls=1 called_by=9 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._select_staff_index` | calls=0 called_by=6 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._select_stadium_index` | calls=0 called_by=6 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._select_player_name` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_name_fields` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_name_fields.apply` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_save_player` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_select_team` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_select_team.apply` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_search_filter` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_search_filter.apply` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_get_team_state` | calls=1 called_by=0 callback_refs=2
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_get_team_state.gather` | calls=0 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_team_field` | calls=1 called_by=0 callback_refs=2
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_team_field.apply` | calls=0 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_team_fields` | calls=1 called_by=0 callback_refs=2
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_team_fields.apply` | calls=0 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_save_team` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_save_team.save` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_refresh_players` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_show_screen` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_show_screen.apply` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_invoke_feature` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_open_full_editor` | calls=3 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_open_full_editor.open_it` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_open_full_staff_editor` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_open_full_staff_editor.open_it` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_open_full_stadium_editor` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_open_full_stadium_editor.open_it` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._invoke_app_method` | calls=0 called_by=1 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_detail_field` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_detail_field.apply` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.list_teams` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.list_staff` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.list_stadiums` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._save_player_and_refresh` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._gather_selection_summary` | calls=0 called_by=4 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._find_open_full_editor` | calls=0 called_by=7 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._find_open_staff_editor` | calls=0 called_by=9 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._find_open_stadium_editor` | calls=0 called_by=9 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._coerce_int` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._get_control_value` | calls=0 called_by=15 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._set_control_value` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_list_full_fields` | calls=3 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_list_full_fields.list_fields` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_full_field` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_full_field.set_field` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._set_full_field_on_ui` | calls=4 called_by=4 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_save_full_editor` | calls=3 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_save_full_editor.save` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_full_fields` | calls=3 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_full_fields.set_many` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_get_full_editor_state` | calls=3 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_get_full_editor_state.state` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_list_staff_fields` | calls=3 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_list_staff_fields.list_fields` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_staff_field` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_staff_field.set_field` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._set_staff_field_on_ui` | calls=4 called_by=4 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_staff_fields` | calls=4 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_staff_fields.set_many` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_save_staff_editor` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_save_staff_editor.save` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_get_staff_editor_state` | calls=3 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_get_staff_editor_state.state` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_list_stadium_fields` | calls=3 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_list_stadium_fields.list_fields` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_stadium_field` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_stadium_field.set_field` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._set_stadium_field_on_ui` | calls=4 called_by=4 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_stadium_fields` | calls=4 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_set_stadium_fields.set_many` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_save_stadium_editor` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_save_stadium_editor.save` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_get_stadium_editor_state` | calls=3 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._cmd_get_stadium_editor_state.state` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._run_on_ui_thread` | calls=1 called_by=38 callback_refs=1
- `nba2k_editor.ai.assistant::LLMControlBridge._run_on_ui_thread.wrapper` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge.server_address` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::LLMControlBridge._detect_screen` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.assistant::ensure_control_bridge` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant.__init__` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._build_panel` | calls=1 called_by=1 callback_refs=3
- `nba2k_editor.ai.assistant::PlayerAIAssistant._refresh_persona_dropdown` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._on_persona_select` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._set_status` | calls=0 called_by=4 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._set_output` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._append_output` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._start_progress` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._stop_progress` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._copy_response` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._get_settings_for_request` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._on_request` | calls=5 called_by=0 callback_refs=1
- `nba2k_editor.ai.assistant::PlayerAIAssistant._run_ai` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._finalize_request` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::PlayerAIAssistant._build_prompt` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ai.assistant::build_local_command` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.assistant::call_local_process` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ai.assistant::call_python_backend` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.ai.assistant::call_remote_api` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ai.assistant::invoke_ai_backend` | calls=3 called_by=2 callback_refs=0

### `nba2k_editor.ai.backend_helpers`
- `nba2k_editor.ai.backend_helpers::<module>` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ai.backend_helpers::load_python_instance` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.backend_helpers::generate_text_sync` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ai.backend_helpers::generate_text_async` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.ai.backends.__init__`
- `nba2k_editor.ai.backends.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ai.backends.base`
- `nba2k_editor.ai.backends.base::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ai.backends.http_backend`
- `nba2k_editor.ai.backends.http_backend::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.backends.http_backend::call_chat_completions` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ai.backends.python_backend`
- `nba2k_editor.ai.backends.python_backend::<module>` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.ai.backends.python_backend::_instance_key` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.backends.python_backend::load_instance` | calls=1 called_by=7 callback_refs=0
- `nba2k_editor.ai.backends.python_backend::generate_sync` | calls=0 called_by=7 callback_refs=0
- `nba2k_editor.ai.backends.python_backend::generate_async` | calls=3 called_by=2 callback_refs=1
- `nba2k_editor.ai.backends.python_backend::generate_async._worker` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ai.backends.python_backend::_emit_chunked` | calls=0 called_by=3 callback_refs=0

### `nba2k_editor.ai.cba_context`
- `nba2k_editor.ai.cba_context::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ai.cba_context::_format_with_citations` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.cba_context::build_cba_guidance` | calls=2 called_by=2 callback_refs=0

### `nba2k_editor.ai.detection`
- `nba2k_editor.ai.detection::<module>` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.ai.detection::_maybe_path` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.ai.detection::_local_ai_candidates` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ai.detection::_local_model_roots` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ai.detection::_iter_model_files` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.detection::detect_local_ai_installations` | calls=3 called_by=0 callback_refs=0

### `nba2k_editor.ai.nba_data`
- `nba2k_editor.ai.nba_data::<module>` | calls=10 called_by=0 callback_refs=0
- `nba2k_editor.ai.nba_data::_normalize_name` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.nba_data::_clean_text` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.nba_data::_to_int` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.ai.nba_data::_to_float` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.nba_data::warm_cache_async` | calls=0 called_by=0 callback_refs=1
- `nba2k_editor.ai.nba_data::ensure_loaded` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ai.nba_data::_load_data` | calls=3 called_by=2 callback_refs=1
- `nba2k_editor.ai.nba_data::get_player_summary` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ai.nba_data::_fmt_num` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.nba_data::_fmt_pct` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ai.nba_data::_format_summary` | calls=4 called_by=2 callback_refs=0
- `nba2k_editor.ai.nba_data::last_error` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ai.personas`
- `nba2k_editor.ai.personas::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.personas::ensure_default_profiles` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.personas::get_persona_text` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.personas::export_profiles` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.personas::import_profiles` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ai.settings`
- `nba2k_editor.ai.settings::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.settings::load_settings` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ai.settings::save_settings` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.core.__init__`
- `nba2k_editor.core.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.core.config`
- `nba2k_editor.core.config::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.core.conversions`
- `nba2k_editor.core.conversions::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.core.conversions::_normalize_year_key` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.conversions::is_year_offset_field` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.core.conversions::convert_raw_to_year` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.core.conversions::convert_year_to_raw` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.conversions::convert_raw_to_rating` | calls=0 called_by=5 callback_refs=0
- `nba2k_editor.core.conversions::convert_rating_to_raw` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.conversions::convert_minmax_potential_to_raw` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.conversions::convert_raw_to_minmax_potential` | calls=0 called_by=5 callback_refs=0
- `nba2k_editor.core.conversions::read_weight` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.conversions::write_weight` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.conversions::raw_height_to_inches` | calls=0 called_by=7 callback_refs=0
- `nba2k_editor.core.conversions::height_inches_to_raw` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.conversions::format_height_inches` | calls=0 called_by=4 callback_refs=0
- `nba2k_editor.core.conversions::convert_tendency_raw_to_rating` | calls=0 called_by=5 callback_refs=0
- `nba2k_editor.core.conversions::convert_rating_to_tendency_raw` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.conversions::to_int` | calls=0 called_by=53 callback_refs=0

### `nba2k_editor.core.dynamic_bases`
- `nba2k_editor.core.dynamic_bases::<module>` | calls=13 called_by=0 callback_refs=0
- `nba2k_editor.core.dynamic_bases::_encode_wstring` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.core.dynamic_bases::_find_process_pid` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.dynamic_bases::_get_module_base` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.dynamic_bases::_iter_memory_regions` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.core.dynamic_bases::_read_memory` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.core.dynamic_bases::_find_all` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.dynamic_bases::_scan_player_names` | calls=5 called_by=2 callback_refs=0
- `nba2k_editor.core.dynamic_bases::_find_team_table` | calls=3 called_by=2 callback_refs=0
- `nba2k_editor.core.dynamic_bases::_summarize_candidates` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.core.dynamic_bases::_scan_players_with_ranges` | calls=1 called_by=2 callback_refs=1
- `nba2k_editor.core.dynamic_bases::_scan_teams_with_ranges` | calls=1 called_by=2 callback_refs=1
- `nba2k_editor.core.dynamic_bases::find_dynamic_bases` | calls=5 called_by=2 callback_refs=2

### `nba2k_editor.core.extensions`
- `nba2k_editor.core.extensions::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.extensions::register_player_panel_extension` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.extensions::register_full_editor_extension` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.extensions::load_autoload_extensions` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.extensions::save_autoload_extensions` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.core.import_map`
- `nba2k_editor.core.import_map::<module>` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.core.import_map::_read_text` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.import_map::_module_name_for` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.import_map::build_import_map` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.core.import_map::write_import_report` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.core.offset_cache`
- `nba2k_editor.core.offset_cache::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_cache::OffsetCache.__init__` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.core.offset_cache::OffsetCache.get_target` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_cache::OffsetCache.set_target` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_cache::OffsetCache.get_json` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_cache::OffsetCache.set_json` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_cache::OffsetCache.get_dropdowns` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_cache::OffsetCache.set_dropdowns` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_cache::OffsetCache.invalidate_target` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_cache::OffsetCache.clear` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.core.offset_loader`
- `nba2k_editor.core.offset_loader::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_loader::OffsetRepository.__init__` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.core.offset_loader::OffsetRepository.load_offsets` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_loader::OffsetRepository.load_dropdowns` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_loader::OffsetRepository._load_raw_json` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.offset_loader::OffsetRepository._parse_dropdowns` | calls=0 called_by=1 callback_refs=0

### `nba2k_editor.core.offset_resolver`
- `nba2k_editor.core.offset_resolver::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offset_resolver::OffsetResolver.__init__` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.core.offset_resolver::OffsetResolver.resolve` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.core.offset_resolver::OffsetResolver.require_dict` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.core.offsets`
- `nba2k_editor.core.offsets::<module>` | calls=32 called_by=0 callback_refs=0
- `nba2k_editor.core.offsets::_derive_offset_candidates` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_split_version_tokens` | calls=0 called_by=4 callback_refs=0
- `nba2k_editor.core.offsets::_version_key_matches` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.core.offsets::_select_version_entry` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_infer_length_bits` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_normalize_offset_type` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_read_json_cached` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_build_dropdown_values_index` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_resolve_split_category` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_collect_split_leaf_nodes` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.core.offsets::_append_split_domain_entries` | calls=3 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_build_split_offsets_payload` | calls=3 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_select_merged_offset_entry` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offsets::_build_player_stats_relations` | calls=2 called_by=2 callback_refs=2
- `nba2k_editor.core.offsets::_build_player_stats_relations._entry_sort_key` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_build_player_stats_relations._id_sort_key` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.core.offsets::_extract_player_stats_relations` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_sync_player_stats_relations` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_convert_merged_offsets_schema` | calls=7 called_by=0 callback_refs=0
- `nba2k_editor.core.offsets::_convert_merged_offsets_schema._record_skip` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.core.offsets::_load_offset_config_file` | calls=3 called_by=2 callback_refs=2
- `nba2k_editor.core.offsets::_build_offset_index` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_find_offset_entry` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offsets::_find_offset_entry_by_normalized` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.core.offsets::_load_dropdowns_map` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_derive_version_label` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_resolve_version_context` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_load_categories` | calls=9 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_load_categories._emit_super_type_warnings` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.core.offsets::_load_categories._register_category_metadata` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.core.offsets::_load_categories._finalize_field_metadata` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.core.offsets::_load_categories._entry_to_field` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.core.offsets::_load_categories._humanize_label` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_load_categories._template_entry_to_field` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_load_categories._compose_field_prefix` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_load_categories._convert_template_payload` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.core.offsets::_load_categories._merge_extra_template_files` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.offsets::_normalize_chain_steps` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_parse_pointer_chain_config` | calls=3 called_by=4 callback_refs=0
- `nba2k_editor.core.offsets::_extend_pointer_candidates` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_normalize_base_pointer_overrides` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_apply_base_pointer_overrides` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_apply_base_pointer_overrides._merge` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.core.offsets::_apply_offset_config` | calls=8 called_by=2 callback_refs=0
- `nba2k_editor.core.offsets::_apply_offset_config._pointer_address` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.core.offsets::_apply_offset_config._require_field` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.core.offsets::initialize_offsets` | calls=7 called_by=8 callback_refs=2

### `nba2k_editor.core.perf`
- `nba2k_editor.core.perf::<module>` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.core.perf::is_enabled` | calls=0 called_by=5 callback_refs=0
- `nba2k_editor.core.perf::record_duration` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.core.perf::timed` | calls=2 called_by=15 callback_refs=0
- `nba2k_editor.core.perf::time_call` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.core.perf::clear` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.core.perf::snapshot` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.core.perf::summarize` | calls=1 called_by=2 callback_refs=0

### `nba2k_editor.entrypoints.__init__`
- `nba2k_editor.entrypoints.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.entrypoints.editor_train_hook`
- `nba2k_editor.entrypoints.editor_train_hook::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.entrypoints.editor_train_hook::run_training_from_editor` | calls=1 called_by=1 callback_refs=0

### `nba2k_editor.entrypoints.extract_cba_rules`
- `nba2k_editor.entrypoints.extract_cba_rules::<module>` | calls=8 called_by=0 callback_refs=0
- `nba2k_editor.entrypoints.extract_cba_rules::_default_source` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.entrypoints.extract_cba_rules::_default_outdir` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.entrypoints.extract_cba_rules::main` | calls=7 called_by=1 callback_refs=0

### `nba2k_editor.entrypoints.gui`
- `nba2k_editor.entrypoints.gui::<module>` | calls=12 called_by=0 callback_refs=0
- `nba2k_editor.entrypoints.gui::_cleanup_enabled` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.entrypoints.gui::_delete_runtime_cache_dirs` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.entrypoints.gui::_print_offsets_status` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.entrypoints.gui::_launch_with_dearpygui` | calls=3 called_by=2 callback_refs=0
- `nba2k_editor.entrypoints.gui::main` | calls=9 called_by=1 callback_refs=0

### `nba2k_editor.entrypoints.train_gm_agent`
- `nba2k_editor.entrypoints.train_gm_agent::<module>` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.__init__`
- `nba2k_editor.gm_rl.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.actions`
- `nba2k_editor.gm_rl.actions::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionSpaceSpec.sizes` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionMask.to` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionMaskBuilder.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionMaskBuilder._record_block` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionMaskBuilder._record_warn` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionMaskBuilder._citation_ids` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionMaskBuilder.build` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionGrammar.__init__` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionGrammar.decode` | calls=7 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionGrammar._rotation_template` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionGrammar._cheapest_player` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionGrammar._trade_pool` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionGrammar._contract_pool` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionGrammar._roster_move` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.actions::ActionGrammar._first_true_index` | calls=0 called_by=1 callback_refs=0

### `nba2k_editor.gm_rl.adapters.__init__`
- `nba2k_editor.gm_rl.adapters.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.adapters.base`
- `nba2k_editor.gm_rl.adapters.base::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.base::TeamState.roster_size` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.base::RosterState.get_team` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.base::RosterState.get_player` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.base::EditorAdapter.load_roster_state` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.base::EditorAdapter.load_league_context` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.base::EditorAdapter.apply_gm_action` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.base::EditorAdapter.get_salary_cap` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.base::EditorAdapter.get_payroll` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.base::safe_ratio` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.adapters.editor_live`
- `nba2k_editor.gm_rl.adapters.editor_live::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_live::_resolve_editor_base_dir` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_live::EditorLiveAdapter.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_live::EditorLiveAdapter.load_roster_state` | calls=0 called_by=4 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_live::EditorLiveAdapter.load_league_context` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_live::EditorLiveAdapter.apply_gm_action` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_live::EditorLiveAdapter.get_salary_cap` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_live::EditorLiveAdapter.get_payroll` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_live::EditorLiveAdapter._make_prospect` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_live::EditorLiveAdapter._swap_players` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_live::EditorLiveAdapter._refresh_payrolls` | calls=0 called_by=1 callback_refs=0

### `nba2k_editor.gm_rl.adapters.editor_state`
- `nba2k_editor.gm_rl.adapters.editor_state::<module>` | calls=6 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_state::_default_context` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_state::_synthetic_stats` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_state::_synthetic_phys` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_state::_clone_stats` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_state::_clone_phys` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_state::_norm_name` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_state::LiveRosterBuilder.__init__` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_state::LiveRosterBuilder.build` | calls=7 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.editor_state::LiveRosterBuilder._fallback_state` | calls=0 called_by=1 callback_refs=0

### `nba2k_editor.gm_rl.adapters.local_mock`
- `nba2k_editor.gm_rl.adapters.local_mock::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::_resolve_editor_base_dir` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter.load_roster_state` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter.load_league_context` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter.apply_gm_action` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter.get_salary_cap` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter.get_payroll` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter._load_players` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter._load_players_from_workbook` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter._synthetic_players` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter._build_teams` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter._swap_players` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter._prospect_stats` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.adapters.local_mock::LocalMockAdapter._prospect_phys` | calls=0 called_by=1 callback_refs=0

### `nba2k_editor.gm_rl.cba.__init__`
- `nba2k_editor.gm_rl.cba.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.cba.docx_reader`
- `nba2k_editor.gm_rl.cba.docx_reader::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::DocxContent.paragraph` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::DocxContent.paragraphs_slice` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::DocxContent.table` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::_norm_text` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::load_docx` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::find_paragraph` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::find_all_paragraphs` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::parse_percent` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::parse_int` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::parse_currency_amount` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::extract_date_token` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.gm_rl.cba.docx_reader::table_data_rows` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.cba.extractors`
- `nba2k_editor.gm_rl.cba.extractors::<module>` | calls=16 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::_now_utc` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::_load_yaml_json` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::load_manifest` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::load_manual_overrides` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::_add_citation` | calls=0 called_by=7 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::_parse_money_rate` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::_extract_cap_rules` | calls=5 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::_extract_cap_rules._parse_tax_table` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::_extract_contract_rules` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::_extract_trade_rules` | calls=3 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::_extract_draft_rules` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::_extract_free_agency_rules` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::_extract_roster_rules` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.extractors::extract_raw_rules` | calls=9 called_by=2 callback_refs=0

### `nba2k_editor.gm_rl.cba.normalizer`
- `nba2k_editor.gm_rl.cba.normalizer::<module>` | calls=5 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.cba.normalizer::_get_nested` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.normalizer::_set_nested` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.normalizer::_apply_overrides` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.normalizer::_validate_required_fields` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.normalizer::_find_unresolved_fields` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.normalizer::_find_unresolved_fields.walk` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.normalizer::normalize_rules` | calls=3 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.normalizer::ruleset_to_all_years_payload` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.gm_rl.cba.repository`
- `nba2k_editor.gm_rl.cba.repository::<module>` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.cba.repository::_cba_dir` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.repository::default_ruleset_path` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.gm_rl.cba.repository::load_ruleset` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.cba.repository::load_ruleset_for_season` | calls=2 called_by=2 callback_refs=0

### `nba2k_editor.gm_rl.cba.schema`
- `nba2k_editor.gm_rl.cba.schema::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.cba.schema::CbaRuleSet.to_dict` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.cba.schema::CbaRuleSet.from_dict` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.cba.section_registry`
- `nba2k_editor.gm_rl.cba.section_registry::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.env`
- `nba2k_editor.gm_rl.env::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.env::NBA2KGMEnv.__init__` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.env::NBA2KGMEnv.reset` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.env::NBA2KGMEnv.step` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.env::NBA2KGMEnv._to_obs_dict` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.env::NBA2KGMEnv._episode_length` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.env::NBA2KGMEnv._build_action_mask` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.env::NBA2KGMEnv._compute_reward` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.env::NBA2KGMEnv._player_value` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.env::SyncVecEnv.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.env::SyncVecEnv.num_envs` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.env::SyncVecEnv.reset` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.env::SyncVecEnv.step` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.env::SyncVecEnv._stack` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.env::make_vec_env` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.eval`
- `nba2k_editor.gm_rl.eval::<module>` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.eval::build_adapter` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.eval::evaluate` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.eval::main` | calls=1 called_by=1 callback_refs=0

### `nba2k_editor.gm_rl.features`
- `nba2k_editor.gm_rl.features::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.features::ObservationBatch.to_torch` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.features::RunningMeanStd.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.features::RunningMeanStd.update` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.features::RunningMeanStd.normalize` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder.__init__` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder.encode` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder._team_features` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder._league_features` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder._player_table` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder._team_dim` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder._league_dim` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder._player_dim` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder._player_row` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder._opt_val` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder._encode_division` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.features::FeatureEncoder._encode_conference` | calls=0 called_by=1 callback_refs=0

### `nba2k_editor.gm_rl.models`
- `nba2k_editor.gm_rl.models::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.models::MaskedCategorical.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.models::MaskedCategorical.entropy` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.models::AttentionPool.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.models::AttentionPool.forward` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.models::GMPolicy.__init__` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.models::GMPolicy.forward` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.models::GMPolicy.act` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.ppo`
- `nba2k_editor.gm_rl.ppo::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.ppo::RolloutBuffer.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.ppo::RolloutBuffer.add` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.ppo::RolloutBuffer.compute_returns_and_advantages` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.ppo::RolloutBuffer.get_batches` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.ppo::RolloutBuffer.reset` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.ppo::PPOTrainer.__init__` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.ppo::PPOTrainer._stack_action_masks` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.ppo::PPOTrainer.train` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.ppo::PPOTrainer._mask_list_from_info` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.ppo::PPOTrainer._log_metrics` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.ppo::PPOTrainer.save_checkpoint` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.runtime`
- `nba2k_editor.gm_rl.runtime::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.runtime::AgentRuntime.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.runtime::AgentRuntime.events` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.runtime::AgentRuntime.stop` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.gm_rl.runtime::AgentRuntime.start_evaluate` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.gm_rl.runtime::AgentRuntime.start_live_assist` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.gm_rl.runtime::AgentRuntime.start_training` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.gm_rl.runtime::AgentRuntime._mask_from_info` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.runtime::AgentRuntime._mask_from_info._to_mask` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.gm_rl.runtime::AgentRuntime._run_evaluate` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.runtime::AgentRuntime._run_live_assist` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.runtime::AgentRuntime._run_training` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.gm_rl.train`
- `nba2k_editor.gm_rl.train::<module>` | calls=5 called_by=0 callback_refs=0
- `nba2k_editor.gm_rl.train::set_seed` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.train::load_config` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.train::save_config` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.train::build_adapter` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.gm_rl.train::main` | calls=4 called_by=4 callback_refs=1
- `nba2k_editor.gm_rl.train::main.env_fn` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.importing.__init__`
- `nba2k_editor.importing.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.importing.excel_import`
- `nba2k_editor.importing.excel_import::<module>` | calls=29 called_by=0 callback_refs=0
- `nba2k_editor.importing.excel_import::_RecordSnapshot.record_view` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.importing.excel_import::_build_player_snapshot` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_decode_string_from_record` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_decode_float_from_record` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_decode_bits_from_record` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_decode_field_value_from_record` | calls=7 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::ImportResult.summary_text` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.importing.excel_import::ExportResult.summary_text` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.importing.excel_import::template_path_for` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_ensure_openpyxl` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.importing.excel_import::_sanitize_excel_value` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_header_text` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_field_text` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.importing.excel_import::_header_candidates` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.importing.excel_import::_preferred_categories` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.importing.excel_import::_build_field_lookup` | calls=2 called_by=3 callback_refs=0
- `nba2k_editor.importing.excel_import::_resolve_version_key` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_augment_with_display_aliases` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_map_headers` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.importing.excel_import::_find_column` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_resolve_row_name` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.importing.excel_import::_build_row_key_map` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_row_has_values` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_resolve_player` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::_resolve_named_index` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.importing.excel_import::import_excel_workbook` | calls=10 called_by=5 callback_refs=0
- `nba2k_editor.importing.excel_import::export_excel_workbook` | calls=9 called_by=5 callback_refs=0
- `nba2k_editor.importing.excel_import::import_players_from_excel` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.importing.excel_import::import_teams_from_excel` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.importing.excel_import::import_staff_from_excel` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.importing.excel_import::import_stadiums_from_excel` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.importing.excel_import::export_players_to_excel` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.importing.excel_import::export_teams_to_excel` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.importing.excel_import::export_staff_to_excel` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.importing.excel_import::export_stadiums_to_excel` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.logs.logging`
- `nba2k_editor.logs.logging::<module>` | calls=20 called_by=0 callback_refs=0
- `nba2k_editor.logs.logging::_null_logger` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.logs.logging::_truthy_env` | calls=0 called_by=5 callback_refs=0
- `nba2k_editor.logs.logging::_int_env` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.logs.logging::_parse_list_env` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.logs.logging::_infer_scan_context` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.logs.logging::_parse_tag_overrides` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.logs.logging::_infer_tag_context` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.logs.logging::_infer_caller` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.logs.logging::_infer_stack` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.logs.logging::_thread_context` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.logs.logging::_ScanContextFilter.filter` | calls=7 called_by=0 callback_refs=0
- `nba2k_editor.logs.logging::_attach_scan_filter` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.logs.logging::_effective_log_dir` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.logs.logging::_file_logger` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.logs.logging::format_event` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.logs.logging::_load_logger_from_path` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.logs.logging::_load_dev_logger` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.logs.logging::get_memory_logger` | calls=5 called_by=1 callback_refs=0
- `nba2k_editor.logs.logging::get_ai_logger` | calls=4 called_by=1 callback_refs=0
- `nba2k_editor.logs.logging::log_ai_event` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.logs.logging::_install_ai_trace` | calls=3 called_by=1 callback_refs=1
- `nba2k_editor.logs.logging::_install_ai_trace._profile` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.memory.__init__`
- `nba2k_editor.memory.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.memory.game_memory`
- `nba2k_editor.memory.game_memory::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory._detect_pointer_size` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory._log_event` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.find_pid` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.open_process` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.close` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory._get_module_base` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory._check_open` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.read_bytes` | calls=2 called_by=4 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.write_bytes` | calls=2 called_by=4 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.write_pointer` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.read_uint32` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.write_uint32` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.read_uint64` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.read_wstring` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.write_wstring_fixed` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.read_ascii` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.memory.game_memory::GameMemory.write_ascii_fixed` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.memory.scan_utils`
- `nba2k_editor.memory.scan_utils::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.memory.scan_utils::encode_wstring` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.memory.scan_utils::find_all` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.memory.win32`
- `nba2k_editor.memory.win32::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.models.__init__`
- `nba2k_editor.models.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.models.data_model`
- `nba2k_editor.models.data_model::<module>` | calls=17 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.__init__` | calls=6 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.mark_dirty` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.clear_dirty` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.is_dirty` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._make_name_key` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._sync_offset_constants` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_name_fields` | calls=6 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_name_fields._string_enc_for_type` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_name_fields._build_field` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_name_fields._find_normalized_field` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_name_fields._log_field` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.invalidate_base_cache` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.prime_bases` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._strip_suffix_string` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._generate_name_keys` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._strip_diacritics` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._sanitize_name_token` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._strip_suffix_words` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._normalize_family_token` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._build_name_index_map` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._build_name_index_map_from_players` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._build_name_index_map_async` | calls=1 called_by=2 callback_refs=1
- `nba2k_editor.models.data_model::PlayerDataModel._build_name_index_map_async._worker` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._match_name_tokens` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._candidate_name_pairs` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._candidate_name_pairs.add_pair` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_categories_for_super` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_league_categories` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._league_context` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._league_stride` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._league_pointer_meta` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._league_pointer_for_category` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_league_base` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_league_records` | calls=5 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_league_records._validator` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._expand_first_name_variants` | calls=3 called_by=3 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._expand_first_name_variants.add` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._expand_last_name_variants` | calls=3 called_by=3 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._expand_last_name_variants.add` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._name_variants` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._match_player_indices` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._token_similarity` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._rank_roster_candidates` | calls=6 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._partial_name_candidates` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.find_player_indices_by_name` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._normalize_field_name` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._normalize_header_name` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._reorder_categories` | calls=4 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._reorder_categories._normalize_field_name_local` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._reorder_categories._reorder_category` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.parse_team_comments` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._player_record_address` | calls=1 called_by=9 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._team_record_address` | calls=1 called_by=6 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._staff_record_address` | calls=1 called_by=5 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._stadium_record_address` | calls=1 called_by=5 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_pointer_from_chain` | calls=1 called_by=5 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_player_base_ptr` | calls=3 called_by=6 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_player_base_ptr._validate_player_table` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_player_table_base` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_team_base_ptr` | calls=3 called_by=11 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_team_base_ptr._is_valid_team_base` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_staff_base_ptr` | calls=5 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_staff_base_ptr._log` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_staff_base_ptr._is_valid_staff_base` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._direct_base_from_chain` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_stadium_base_ptr` | calls=4 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_stadium_base_ptr._is_valid_stadium_base` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._scan_team_names` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_team_fields` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.set_team_fields` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._scan_all_players` | calls=7 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._scan_all_players._decode_string` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._scan_all_players._read_uint64` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._scan_all_players._read_uint32` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._scan_all_players._is_ascii_printable` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.scan_team_players` | calls=5 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._team_display_map` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._team_index_for_display_name` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._get_team_display_name` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_teams` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_teams._classify` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.refresh_staff` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_staff` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.refresh_stadiums` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_stadiums` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._build_team_display_list` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._ensure_team_entry` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._build_team_list_from_players` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._apply_team_display_to_players` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._read_panel_entry` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_player_panel_snapshot` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._collect_assigned_player_indexes` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.refresh_players` | calls=9 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_players_by_team` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.update_player` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.copy_player_data` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._normalize_encoding_tag` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._read_string` | calls=1 called_by=14 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._write_string` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._effective_byte_length` | calls=0 called_by=10 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._normalize_field_type` | calls=0 called_by=9 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._is_string_type` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._string_encoding_for_type` | calls=1 called_by=5 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._is_float_type` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._is_pointer_type` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._is_color_type` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._extract_field_parts` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_entity_address` | calls=4 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._resolve_field_address` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._read_entity_field_typed` | calls=4 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._write_entity_field_typed` | calls=4 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._parse_int_value` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._parse_float_value` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._parse_hex_value` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._clamp_enum_index` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._format_hex_value` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._is_team_pointer_field` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._team_pointer_to_display_name` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._team_display_name_to_pointer` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._coerce_field_value` | calls=18 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.coerce_field_value` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.decode_field_value` | calls=23 called_by=3 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.decode_field_value_from_buffer` | calls=19 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.encode_field_value` | calls=8 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._load_external_roster` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_field_value` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_field_value_typed` | calls=3 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_team_field_value` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._write_field_bits` | calls=0 called_by=5 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._apply_field_assignments` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.set_field_value` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.set_field_value_typed` | calls=3 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.set_team_field_value` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_team_field_value_typed` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.set_team_field_value_typed` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_staff_field_value` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_staff_field_value_typed` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.set_staff_field_value` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.set_staff_field_value_typed` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_stadium_field_value` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_stadium_field_value_typed` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.set_stadium_field_value` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.set_stadium_field_value_typed` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._player_flag_entry` | calls=0 called_by=4 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._read_player_flag` | calls=4 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.is_player_draft_prospect` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.is_player_hidden` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_draft_prospects` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.is_player_free_agent_group` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel.get_free_agents_by_flags` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.models.data_model::PlayerDataModel._get_free_agents` | calls=4 called_by=2 callback_refs=0

### `nba2k_editor.models.player`
- `nba2k_editor.models.player::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.player::Player.full_name` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.player::Player.__repr__` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.models.schema`
- `nba2k_editor.models.schema::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.models.services.__init__`
- `nba2k_editor.models.services.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.models.services.io_codec`
- `nba2k_editor.models.services.io_codec::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.io_codec::IOCodec.__init__` | calls=0 called_by=8 callback_refs=0
- `nba2k_editor.models.services.io_codec::IOCodec.get_player` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.io_codec::IOCodec.set_player` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.io_codec::IOCodec.get_team` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.io_codec::IOCodec.set_team` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.io_codec::IOCodec.get_staff` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.io_codec::IOCodec.set_staff` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.io_codec::IOCodec.get_stadium` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.io_codec::IOCodec.set_stadium` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.models.services.player_service`
- `nba2k_editor.models.services.player_service::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.services.player_service::PlayerService.__init__` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.services.player_service::PlayerService.refresh` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.player_service::PlayerService.get_field` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.player_service::PlayerService.set_field` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.models.services.stadium_service`
- `nba2k_editor.models.services.stadium_service::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.services.stadium_service::StadiumService.__init__` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.services.stadium_service::StadiumService.refresh` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.stadium_service::StadiumService.get_field` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.stadium_service::StadiumService.set_field` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.models.services.staff_service`
- `nba2k_editor.models.services.staff_service::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.services.staff_service::StaffService.__init__` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.services.staff_service::StaffService.refresh` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.staff_service::StaffService.get_field` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.staff_service::StaffService.set_field` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.models.services.team_service`
- `nba2k_editor.models.services.team_service::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.services.team_service::TeamService.__init__` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.models.services.team_service::TeamService.refresh` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.team_service::TeamService.get_fields` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.team_service::TeamService.set_fields` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.team_service::TeamService.get_field` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.models.services.team_service::TeamService.set_field` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_action_legality`
- `nba2k_editor.tests.test_action_legality::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_action_legality::test_draft_mask_blocks_full_roster` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_action_legality::test_roster_move_mask_respects_minimum` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_async_exception_callbacks`
- `nba2k_editor.tests.test_async_exception_callbacks::<module>` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_CallbackAppStub.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_CallbackAppStub.run_on_ui_thread` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_AssistantPanelStub.__init__` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_AssistantPanelStub._finalize_request` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_AssistantPanelStub._append_output` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_DynamicScanStub.__init__` | calls=0 called_by=4 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_DynamicScanStub._hook_label_for` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_DynamicScanStub._set_dynamic_scan_status` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_DynamicScanStub.run_on_ui_thread` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_DynamicScanStub.show_error` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_DynamicScanStub.show_warning` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_DynamicScanStub.show_info` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_DynamicScanStub._update_status` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_DynamicScanStub._start_scan` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::_run_ui_callbacks` | calls=0 called_by=5 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::test_ai_panel_deferred_error_callback_preserves_exception_message` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_async_exception_callbacks::test_ai_panel_deferred_error_callback_preserves_exception_message._raise_backend` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::test_dynamic_scan_offsets_load_error_callback_survives_exception_scope` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_async_exception_callbacks::test_dynamic_scan_offsets_load_error_callback_survives_exception_scope._raise_offsets` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::test_dynamic_scan_failure_warning_callback_survives_exception_scope` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_async_exception_callbacks::test_dynamic_scan_failure_warning_callback_survives_exception_scope._raise_scan` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_async_exception_callbacks::test_dynamic_apply_failure_warning_callback_survives_exception_scope` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_async_exception_callbacks::test_dynamic_apply_failure_warning_callback_survives_exception_scope._init_offsets` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_cba_action_legality`
- `nba2k_editor.tests.test_cba_action_legality::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_cba_action_legality::_ruleset` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.tests.test_cba_action_legality::test_cba_blocks_trade_after_deadline_and_emits_warning` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_cba_action_legality::test_cba_blocks_contracts_when_hard_cap_reached` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_cba_assistant_context`
- `nba2k_editor.tests.test_cba_assistant_context::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_cba_assistant_context::test_cba_guidance_contains_core_constraints` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_cba_extraction`
- `nba2k_editor.tests.test_cba_extraction::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_cba_extraction::_source_doc` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_cba_extraction::test_cba_extraction_core_constants_and_tables` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_data_model_category_grouping`
- `nba2k_editor.tests.test_data_model_category_grouping::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_data_model_category_grouping::test_get_categories_for_super_groups_player_categories` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_editor_live_adapter`
- `nba2k_editor.tests.test_editor_live_adapter::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_editor_live_adapter::_StubMem.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_editor_live_adapter::_StubMem.open_process` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_editor_live_adapter::_StubModel.__init__` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.tests.test_editor_live_adapter::_StubModel.refresh_players` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_editor_live_adapter::_StubModel._build_team_list_from_players` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_editor_live_adapter::test_live_adapter_builds_roster_from_stub` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_editor_live_adapter::test_rotation_minutes_cap_enforced` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_editor_live_adapter::test_trade_swaps_rosters` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_excel_callbacks_regression`
- `nba2k_editor.tests.test_excel_callbacks_regression::<module>` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ContextStub.__enter__` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ContextStub.__exit__` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ExcelScreenAppStub.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ExcelScreenAppStub._import_excel` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ExcelScreenAppStub._export_excel` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ExcelAppStub.__init__` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ExcelAppStub.show_error` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ExcelAppStub.show_info` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_VarStub.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_VarStub.set` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_VarStub.get` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ExportFinishAppStub.__init__` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ExportFinishAppStub._reset_excel_progress` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ExportFinishAppStub._set_excel_status` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ExportFinishAppStub.show_info` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_ExportFinishAppStub.show_error` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::test_excel_section_callbacks_ignore_user_data` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_excel_callbacks_regression::test_excel_section_callbacks_ignore_user_data._fake_add_button` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::test_import_excel_blank_entity_reports_error` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::test_export_excel_blank_entity_reports_error` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::test_open_file_dialog_uses_add_file_extension_filters` | calls=0 called_by=0 callback_refs=2
- `nba2k_editor.tests.test_excel_callbacks_regression::test_open_file_dialog_uses_add_file_extension_filters._fake_add_file_dialog` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::test_open_file_dialog_uses_add_file_extension_filters._fake_add_file_extension` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::test_finish_excel_export_success_keeps_completion_visible` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_excel_callbacks_regression::_Result.test_finish_excel_export_success_keeps_completion_visible.summary_text` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_features`
- `nba2k_editor.tests.test_features::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_features::test_feature_shapes_and_masks` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_features::test_nan_imputation_and_masks` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_full_player_editor_int_bounds`
- `nba2k_editor.tests.test_full_player_editor_int_bounds::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_full_player_editor_int_bounds::test_sanitize_input_int_range_clamps_to_dpg_int_bounds` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_full_player_editor_int_bounds::test_add_field_control_caps_large_integer_bit_length` | calls=0 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_full_player_editor_int_bounds::test_add_field_control_caps_large_integer_bit_length._fake_add_input_int` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_full_player_editor_stats_slots`
- `nba2k_editor.tests.test_full_player_editor_stats_slots::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_full_player_editor_stats_slots::test_prepare_stats_tabs_keeps_career_and_season_awards_merge` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_full_player_editor_stats_slots::test_prepare_stats_tabs_adds_season_slot_selector_and_hides_stats_ids` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_gm_rl_integration`
- `nba2k_editor.tests.test_gm_rl_integration::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_gm_rl_integration::test_gm_rl_alias_points_to_integrated_package` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_io_codec_services`
- `nba2k_editor.tests.test_io_codec_services::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_io_codec_services::_StubModel.__init__` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.tests.test_io_codec_services::_StubModel.mark_dirty` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_io_codec_services::_StubModel.get_field_value_typed` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_io_codec_services::_StubModel.set_field_value_typed` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_io_codec_services::_StubModel.get_team_field_value_typed` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_io_codec_services::_StubModel.set_team_field_value_typed` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_io_codec_services::_StubModel.get_team_fields` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_io_codec_services::_StubModel.set_team_fields` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_io_codec_services::_StubModel.refresh_players` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_io_codec_services::test_io_codec_routes_player_and_team_calls` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_io_codec_services::test_services_mark_dirty_on_writes` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_offsets_services`
- `nba2k_editor.tests.test_offsets_services::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_offsets_services::test_offset_cache_target_roundtrip` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_offsets_services::test_offset_resolver_prefers_converted_payload` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_offsets_services::test_offset_resolver_require_dict_raises` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_offsets_services::test_offset_repository_loads_and_caches` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_offsets_services::test_initialize_offsets_applies_explicit_filename_even_when_target_cached` | calls=0 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_offsets_services::test_initialize_offsets_applies_explicit_filename_even_when_target_cached._fake_apply_offset_config` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_perf_data_model`
- `nba2k_editor.tests.test_perf_data_model::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_data_model::_StubMem.__init__` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.tests.test_perf_data_model::_StubMem.open_process` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_data_model::test_data_model_refresh_perf_harness` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_data_model::test_data_model_init_reuses_loaded_offsets_for_same_target` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_perf_data_model::test_data_model_init_reuses_loaded_offsets_for_same_target._fake_initialize_offsets` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_perf_import`
- `nba2k_editor.tests.test_perf_import::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_import::_StubModel.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_perf_import::_StubModel.get_categories_for_super` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_import::_StubModel.encode_field_value` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_import::_StubModel.decode_field_value` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_import::_build_workbook` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_perf_import::test_import_export_perf_harness` | calls=2 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_perf_startup`
- `nba2k_editor.tests.test_perf_startup::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_startup::_StubMem.__init__` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_startup::_StubMem.open_process` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_startup::_StubModel.__init__` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_startup::_StubApp.__init__` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_perf_startup::test_gui_startup_perf_harness` | calls=0 called_by=0 callback_refs=3
- `nba2k_editor.tests.test_perf_startup::test_gui_startup_does_not_reinitialize_offsets_in_model` | calls=0 called_by=0 callback_refs=3
- `nba2k_editor.tests.test_perf_startup::test_gui_startup_does_not_reinitialize_offsets_in_model._fake_initialize_offsets` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_ppo_math`
- `nba2k_editor.tests.test_ppo_math::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ppo_math::_dummy_obs` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_ppo_math::_dummy_mask` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_ppo_math::test_gae_shapes_and_last_step` | calls=2 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_rollout_buffer`
- `nba2k_editor.tests.test_rollout_buffer::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_rollout_buffer::make_mask` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_rollout_buffer::test_rollout_buffer_ordering_and_dones` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_runtime_smoke`
- `nba2k_editor.tests.test_runtime_smoke::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_runtime_smoke::test_runtime_mask_from_info_smoke` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_runtime_smoke::test_ppo_mask_stack_smoke` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_scan_entrypoint_compat`
- `nba2k_editor.tests.test_scan_entrypoint_compat::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::_ScanModelStub.__init__` | calls=0 called_by=5 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::_ScanModelStub.refresh_players` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::_ScanModelStub.get_teams` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::_ScanAppStub.__init__` | calls=0 called_by=5 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::_ScanAppStub._update_team_dropdown` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::_ScanAppStub._refresh_player_list` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::_ScanAppStub._on_team_edit_selected` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::_ScanAppStub._render_player_list` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::test_start_scan_wrapper_uses_shared_flow_without_regression` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::test_start_team_scan_wrapper_preserves_pending_selection_behavior` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::test_scan_thread_wrapper_handles_refresh_failure_without_stalling` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_scan_entrypoint_compat::test_scan_teams_thread_wrapper_handles_refresh_failure_without_stalling` | calls=2 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_split_offsets_fidelity`
- `nba2k_editor.tests.test_split_offsets_fidelity::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_split_offsets_fidelity::_load_2k26_config` | calls=0 called_by=7 callback_refs=0
- `nba2k_editor.tests.test_split_offsets_fidelity::_offset_entries` | calls=0 called_by=6 callback_refs=0
- `nba2k_editor.tests.test_split_offsets_fidelity::test_stats_table_categories_are_emitted_without_flat_stats_alias` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_split_offsets_fidelity::test_player_stats_relations_link_ids_to_season_only` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_split_offsets_fidelity::test_parse_report_accounts_for_all_discovered_leaf_fields` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_split_offsets_fidelity::test_type_normalization_covers_observed_player_types` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_split_offsets_fidelity::test_split_entries_include_traceability_and_inference_metadata` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_split_offsets_fidelity::test_version_metadata_preserves_non_core_selected_version_keys` | calls=2 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_startup_load_order`
- `nba2k_editor.tests.test_startup_load_order::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_startup_load_order::_StubMem.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_startup_load_order::_StubMem.open_process` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_startup_load_order::_AppModelStub.__init__` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.tests.test_startup_load_order::_AppModelStub.get_teams` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_startup_load_order::test_model_init_does_not_reinitialize_offsets_for_loaded_target` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_startup_load_order::test_model_init_does_not_reinitialize_offsets_for_loaded_target._fake_initialize_offsets` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_startup_load_order::test_show_ai_builds_screen_and_starts_bridge_lazily` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_startup_load_order::test_show_ai_builds_screen_and_starts_bridge_lazily._fake_build_ai` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_startup_load_order::test_show_ai_builds_screen_and_starts_bridge_lazily._fake_start_bridge` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_startup_load_order::test_show_agent_starts_polling_only_after_screen_is_opened` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_startup_load_order::test_show_agent_starts_polling_only_after_screen_is_opened._fake_build_agent` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_startup_load_order::test_show_agent_starts_polling_only_after_screen_is_opened._fake_start_polling` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_stats_tab_routing`
- `nba2k_editor.tests.test_stats_tab_routing::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_stats_tab_routing::test_prepare_stats_tabs_duplicates_awards_into_career_and_season` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_stats_tab_routing::test_prepare_stats_tabs_replaces_stats_ids_with_season_slot_dropdown` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_stats_tab_routing::test_league_pointer_for_career_category_uses_career_stats_pointer` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_stats_tab_routing::test_league_pointer_for_career_category_uses_career_stats_pointer._fake_pointer_meta` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_stats_tab_routing::test_league_pointer_for_season_category_uses_nba_history_pointer` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_stats_tab_routing::test_league_pointer_for_season_category_uses_nba_history_pointer._fake_pointer_meta` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_strict_offset_mapping`
- `nba2k_editor.tests.test_strict_offset_mapping::<module>` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::restore_offsets_state` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::_entry` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::_strict_offsets_payload` | calls=1 called_by=6 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::_new_league_model_stub` | calls=0 called_by=6 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_apply_offset_config_accepts_exact_mapping_for_all_base_pointer_keys` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_apply_offset_config_rejects_case_variant_base_pointer_key` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_apply_offset_config_rejects_case_variant_size_key` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_apply_offset_config_fails_when_required_size_missing` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_apply_offset_config_does_not_fallback_to_team_stadium_for_stadium_name` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_league_pointer_meta_ignores_case_variant_pointer_keys` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_league_stride_requires_exact_mapped_size_key` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_resolve_version_context_prefers_top_level_base_pointers_and_version_game_info` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_resolve_version_context_falls_back_to_version_base_pointers_when_top_level_missing` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_league_context_delegates_to_offsets_resolver` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_strict_offset_mapping::test_league_context_delegates_to_offsets_resolver._fake_resolve` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_league_pointer_meta_does_not_build_fallback_chain_when_parser_returns_empty` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_strict_offset_mapping::test_league_pointer_meta_uses_canonical_parser_output` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_team_pointer_field_behavior`
- `nba2k_editor.tests.test_team_pointer_field_behavior::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_team_pointer_field_behavior::test_decode_team_pointer_field_displays_team_name` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_team_pointer_field_behavior::test_decode_non_team_pointer_field_stays_hex` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_team_pointer_field_behavior::test_encode_team_pointer_field_accepts_team_name` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_team_pointer_field_behavior::test_encode_team_pointer_field_accepts_team_name._capture_write` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_trade_state`
- `nba2k_editor.tests.test_trade_state::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_trade_state::test_trade_state_add_and_package_projection` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_trade_state::test_trade_state_prevents_duplicates_and_remove` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_trade_state::test_trade_state_clear_slot` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.tests.test_ui_screen_loading_regression`
- `nba2k_editor.tests.test_ui_screen_loading_regression::<module>` | calls=5 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_ScanModelStub.__init__` | calls=0 called_by=6 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_ScanModelStub.refresh_players` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_ScanModelStub.get_teams` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_ScanAppStub.__init__` | calls=0 called_by=6 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_ScanAppStub.run_on_ui_thread` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_ScanAppStub._update_team_dropdown` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_ScanAppStub._refresh_player_list` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_ScanAppStub._on_team_edit_selected` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_ScanAppStub._render_player_list` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_TradeModelStub.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_TradeModelStub.refresh_players` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_TradeAppStub.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_TradeAppStub._trade_ensure_slot_entries` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_TradeAppStub._trade_render_team_lists` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_AppModelStub.__init__` | calls=0 called_by=6 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_AppModelStub.get_teams` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::_LegacyLeagueCategoryModelStub.get_categories_for_super` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_scan_thread_updates_ui_on_success` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_scan_thread_handles_refresh_failure_without_stalling` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_scan_teams_thread_handles_refresh_failure_without_stalling` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_trade_refresh_team_options_bootstraps_from_refresh` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_show_ai_builds_screen_and_bridge_lazily` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_show_ai_builds_screen_and_bridge_lazily._fake_build_ai` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_show_ai_builds_screen_and_bridge_lazily._fake_start_bridge` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_show_agent_builds_screen_and_starts_polling_lazily` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_show_agent_builds_screen_and_starts_polling_lazily._fake_build_agent` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_show_agent_builds_screen_and_starts_polling_lazily._fake_start_polling` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_show_nba_history_routes_to_history_page_and_refreshes` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_show_nba_records_routes_to_records_page_and_refreshes` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_show_league_alias_routes_to_nba_history_page` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_ensure_league_categories_splits_legacy_league_supertype` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_start_scan_uses_shared_scan_flow` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.tests.test_ui_screen_loading_regression::test_start_team_scan_applies_pending_selection_via_shared_flow` | calls=2 called_by=0 callback_refs=0

### `nba2k_editor.ui.__init__`
- `nba2k_editor.ui.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ui.agent_screen`
- `nba2k_editor.ui.agent_screen::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.agent_screen::build_agent_screen` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ui.ai_screen`
- `nba2k_editor.ui.ai_screen::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.ai_screen::build_ai_screen` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ui.app`
- `nba2k_editor.ui.app::<module>` | calls=32 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::BoundVar.__init__` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::BoundVar.get` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::BoundVar.set` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::BoundDoubleVar.get` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::BoundDoubleVar.set` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::BoundBoolVar.get` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::BoundBoolVar.set` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.__init__` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._queue_on_main` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.after` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.run_on_ui_thread` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.enqueue_ui_update` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.destroy` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.build_ui` | calls=13 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._build_sidebar` | calls=0 called_by=1 callback_refs=14
- `nba2k_editor.ui.app::PlayerEditorApp._show_screen` | calls=1 called_by=11 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._ensure_screen_built` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_home` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_players` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_teams` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_nba_history` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_nba_records` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_league` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._ensure_control_bridge_started` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_ai` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_agent` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_trade_players` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_staff` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_stadium` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_excel` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._update_status` | calls=0 called_by=4 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._set_dynamic_scan_status` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._set_offset_status` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.copy_to_clipboard` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._show_modal` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._show_modal._close_dialog` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_info` | calls=1 called_by=17 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_warning` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.show_error` | calls=1 called_by=19 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_file_dialog` | calls=1 called_by=8 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_file_dialog._close` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_file_dialog._on_select` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._start_control_bridge` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._load_ai_settings_into_vars` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._load_ai_settings` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._merge_dict` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._get_ai_profiles` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._ensure_ai_profiles` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._get_team_profiles` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._collect_ai_settings` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.get_ai_settings` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._coerce_int` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._save_ai_settings` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.get_persona_choice_items` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._render_player_list` | calls=0 called_by=2 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._start_scan` | calls=0 called_by=6 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._scan_thread` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._start_roster_scan` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._run_roster_scan` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._run_roster_scan.update_ui` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._refresh_player_list` | calls=3 called_by=4 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._filter_player_list` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._on_team_selected` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._on_player_selected` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._update_detail_fields` | calls=2 called_by=3 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._save_player` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_full_editor` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_copy_dialog` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._export_selected_player` | calls=5 called_by=0 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._export_selected_player._after_choose` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._export_selected_player._after_choose._run_export` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._import_selected_player` | calls=7 called_by=0 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._import_selected_player._after_choose` | calls=6 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.get_player_list_items` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.get_selected_player_indices` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.set_selected_player_indices` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.clear_player_selection` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._ensure_team_listbox` | calls=0 called_by=1 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._start_team_scan` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._scan_teams_thread` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._update_team_dropdown` | calls=2 called_by=3 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._update_team_dropdown._append_unique` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._filter_team_list` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._on_team_listbox_select` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._on_team_edit_selected` | calls=1 called_by=5 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._on_team_field_changed` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._save_team` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_full_team_editor` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._league_state` | calls=0 called_by=7 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._is_nba_records_category` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._filter_league_page_categories` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._register_league_widgets` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._on_league_category_selected` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._ensure_league_categories` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._update_league_status` | calls=1 called_by=1 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._clear_league_table` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._render_league_table` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._refresh_league_records` | calls=5 called_by=3 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._current_staff_index` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._refresh_staff_list` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._filter_staff_list` | calls=0 called_by=1 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._on_staff_selected` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_full_staff_editor` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.get_staff_list_items` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.get_selected_staff_indices` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.set_staff_selection` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._current_stadium_index` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._refresh_stadium_list` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._filter_stadium_list` | calls=0 called_by=1 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._on_stadium_selected` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_full_stadium_editor` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.get_stadium_list_items` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.get_selected_stadium_indices` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp.set_stadium_selection` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_randomizer` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_team_shuffle` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_batch_edit` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_team_player_editor` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._on_team_player_selected` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._update_team_players` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._set_excel_status` | calls=0 called_by=6 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._reset_excel_progress` | calls=0 called_by=10 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._apply_excel_progress` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._excel_progress_callback` | calls=2 called_by=4 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._excel_progress_callback._callback` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._queue_excel_export_progress` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._poll_excel_export` | calls=3 called_by=5 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._finish_excel_export` | calls=4 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._import_excel` | calls=9 called_by=0 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._import_excel._after_choose` | calls=7 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._export_excel` | calls=10 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._export_excel._start_export` | calls=5 called_by=1 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._export_excel._start_export._after_choose` | calls=4 called_by=0 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._export_excel._start_export._after_choose._run_export` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_import_dialog` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_export_dialog` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_load_excel` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._hook_label_for` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._set_hook_target` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._open_offset_file_dialog` | calls=7 called_by=0 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._open_offset_file_dialog._after_choose` | calls=6 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._start_dynamic_base_scan` | calls=1 called_by=0 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._run_dynamic_base_scan` | calls=8 called_by=0 callback_refs=2
- `nba2k_editor.ui.app::PlayerEditorApp._refresh_trade_data` | calls=4 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_refresh_team_options` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_get_roster` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_load_contracts` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_player_label` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_y1_salary` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_refresh_rosters` | calls=2 called_by=4 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_set_active_team` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_set_active_team_from_list` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_add_participant` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_select_active_player` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_open_player_modal` | calls=3 called_by=0 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._trade_open_player_modal._confirm` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_add_transaction` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_clear` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_swap_teams` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_refresh_package_lists` | calls=1 called_by=7 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_update_status` | calls=0 called_by=8 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_select_transaction` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_remove_transaction` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_select_slot` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_clear_slot` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_propose` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_render_team_lists` | calls=2 called_by=3 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._trade_ensure_slot_entries` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._ensure_agent_runtime` | calls=2 called_by=3 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._build_agent_adapter` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._agent_refresh_snapshot` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._agent_start_evaluate` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._agent_start_live_assist` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._agent_start_training` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._agent_stop_runtime` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._agent_pick_checkpoint` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._agent_pick_config` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._set_agent_checkpoint` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._set_agent_config` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._set_agent_status` | calls=0 called_by=6 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._append_agent_log` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.app::PlayerEditorApp._start_agent_polling` | calls=1 called_by=1 callback_refs=1
- `nba2k_editor.ui.app::PlayerEditorApp._poll_agent_events` | calls=3 called_by=0 callback_refs=1

### `nba2k_editor.ui.batch_edit`
- `nba2k_editor.ui.batch_edit::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow.__init__` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow._build_ui` | calls=5 called_by=1 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow._on_category_selected` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow._on_field_selected` | calls=3 called_by=2 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow._apply_changes` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow._reset_core_fields` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow._reset_core_fields.collect_numeric_fields` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow._reset_core_fields._queue_assignment` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow._clear_value_input` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow._field_def` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow._team_names` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.batch_edit::BatchEditWindow._selected_teams` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.batch_edit::open_batch_edit` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.ui.context_menu`
- `nba2k_editor.ui.context_menu::<module>` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.ui.context_menu::attach_player_context_menu` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.context_menu::attach_team_context_menu` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.context_menu::_select_player_and` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.context_menu::_select_team_and` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.context_menu::_ensure_player_selected` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.context_menu::_ensure_team_selected` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.controllers.__init__`
- `nba2k_editor.ui.controllers.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ui.controllers.entity_edit`
- `nba2k_editor.ui.controllers.entity_edit::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.controllers.entity_edit::coerce_int` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.controllers.import_export`
- `nba2k_editor.ui.controllers.import_export::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.controllers.import_export::normalize_entity_key` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.ui.controllers.import_export::entity_title` | calls=0 called_by=6 callback_refs=0

### `nba2k_editor.ui.controllers.navigation`
- `nba2k_editor.ui.controllers.navigation::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.controllers.navigation::show_screen` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.controllers.trade`
- `nba2k_editor.ui.controllers.trade::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.controllers.trade::format_trade_summary` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.dialogs`
- `nba2k_editor.ui.dialogs::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.dialogs::_rgba` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.dialogs::ImportSummaryDialog.__init__` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.ui.dialogs::ImportSummaryDialog._build_ui` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.ui.dialogs::ImportSummaryDialog._initial_suggestion` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.dialogs::ImportSummaryDialog._apply` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.dialogs::CategorySelectionDialog.__init__` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.dialogs::CategorySelectionDialog._build_ui` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.dialogs::CategorySelectionDialog._finish` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.dialogs::TeamSelectionDialog.__init__` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.ui.dialogs::TeamSelectionDialog._normalize_teams` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.dialogs::TeamSelectionDialog._build_ui` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.ui.dialogs::TeamSelectionDialog._toggle_all` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.dialogs::TeamSelectionDialog._toggle_range` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.dialogs::TeamSelectionDialog._sync_checkbox_states` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.dialogs::TeamSelectionDialog._finish` | calls=0 called_by=1 callback_refs=0

### `nba2k_editor.ui.excel_screen`
- `nba2k_editor.ui.excel_screen::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.excel_screen::build_excel_screen` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.excel_screen::_add_section` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.extensions_ui`
- `nba2k_editor.ui.extensions_ui::<module>` | calls=12 called_by=0 callback_refs=0
- `nba2k_editor.ui.extensions_ui::_module_key` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.extensions_ui::_key_to_module_name` | calls=0 called_by=4 callback_refs=0
- `nba2k_editor.ui.extensions_ui::_key_to_path` | calls=0 called_by=4 callback_refs=0
- `nba2k_editor.ui.extensions_ui::_normalize_autoload_key` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.extensions_ui::extension_label_for_key` | calls=2 called_by=3 callback_refs=0
- `nba2k_editor.ui.extensions_ui::_build_restart_command` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.extensions_ui::reload_with_selected_extensions` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.ui.extensions_ui::_load_extensions_from_keys` | calls=3 called_by=2 callback_refs=0
- `nba2k_editor.ui.extensions_ui::autoload_extensions_from_file` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.extensions_ui::discover_extension_files` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.extensions_ui::is_extension_loaded` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.ui.extensions_ui::load_extension_module` | calls=3 called_by=3 callback_refs=0
- `nba2k_editor.ui.extensions_ui::toggle_extension_module` | calls=3 called_by=0 callback_refs=0

### `nba2k_editor.ui.full_player_editor`
- `nba2k_editor.ui.full_player_editor::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor.__init__` | calls=3 called_by=3 callback_refs=2
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._build_tabs` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._clone_fields_with_source` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._stats_id_sort_key` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._build_season_slot_selector_field` | calls=1 called_by=1 callback_refs=1
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._prepare_stats_tabs` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._build_category_tab` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._add_field_control` | calls=3 called_by=1 callback_refs=1
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._load_all_values_async` | calls=4 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._apply_loaded_values` | calls=3 called_by=2 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._save_all` | calls=4 called_by=0 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._get_ui_value` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._is_season_slot_selector_field` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._is_season_stats_field` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._selected_season_slot_index` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._season_stats_base_and_stride` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._resolve_selected_season_record_ptr` | calls=3 called_by=3 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._set_control_default_value` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._load_selected_season_stats_values` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._on_season_slot_changed` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._adjust_category` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._mark_unsaved` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._coerce_int` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._clamp_dpg_int` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._sanitize_input_int_range` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._color_tuple` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._normalize_players` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_player_editor::FullPlayerEditor._on_close` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ui.full_stadium_editor`
- `nba2k_editor.ui.full_stadium_editor::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor.__init__` | calls=2 called_by=2 callback_refs=2
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._build_tabs` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._build_category_tab` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._add_field_control` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._load_all_values_async` | calls=1 called_by=1 callback_refs=1
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._load_all_values_async._worker` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._load_all_values_async._worker._apply` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._apply_loaded_values` | calls=2 called_by=3 callback_refs=0
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._save_all` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._get_ui_value` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._mark_unsaved` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._coerce_int` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_stadium_editor::FullStadiumEditor._on_close` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ui.full_staff_editor`
- `nba2k_editor.ui.full_staff_editor::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor.__init__` | calls=2 called_by=2 callback_refs=2
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._build_tabs` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._build_category_tab` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._add_field_control` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._load_all_values_async` | calls=1 called_by=1 callback_refs=1
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._load_all_values_async._worker` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._load_all_values_async._worker._apply` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._apply_loaded_values` | calls=2 called_by=3 callback_refs=0
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._save_all` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._get_ui_value` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._mark_unsaved` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._coerce_int` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_staff_editor::FullStaffEditor._on_close` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ui.full_team_editor`
- `nba2k_editor.ui.full_team_editor::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.full_team_editor::FullTeamEditor.__init__` | calls=2 called_by=2 callback_refs=2
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._build_tabs` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._build_category_tab` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._add_field_control` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._load_all_values_async` | calls=1 called_by=1 callback_refs=1
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._load_all_values_async._worker` | calls=2 called_by=0 callback_refs=1
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._load_all_values_async._worker._apply` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._apply_loaded_values` | calls=2 called_by=3 callback_refs=0
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._save_all` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._get_ui_value` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._mark_unsaved` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._coerce_int` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.full_team_editor::FullTeamEditor._on_close` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ui.home_screen`
- `nba2k_editor.ui.home_screen::<module>` | calls=3 called_by=0 callback_refs=0
- `nba2k_editor.ui.home_screen::build_home_screen` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.ui.home_screen::_build_home_overview_tab` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.ui.home_screen::_build_home_overview_tab.refresh_status` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.home_screen::_build_home_ai_settings_tab` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.home_screen::_build_extension_loader` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.league_screen`
- `nba2k_editor.ui.league_screen::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.league_screen::build_nba_history_screen` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.league_screen::build_nba_records_screen` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.league_screen::_build_league_screen` | calls=1 called_by=3 callback_refs=0
- `nba2k_editor.ui.league_screen::_on_category_selected` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.players_screen`
- `nba2k_editor.ui.players_screen::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.players_screen::build_players_screen` | calls=2 called_by=2 callback_refs=0
- `nba2k_editor.ui.players_screen::_on_search_changed` | calls=0 called_by=2 callback_refs=0
- `nba2k_editor.ui.players_screen::_build_player_detail_panel` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.randomizer`
- `nba2k_editor.ui.randomizer::<module>` | calls=2 called_by=0 callback_refs=0
- `nba2k_editor.ui.randomizer::RandomizerWindow.__init__` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.ui.randomizer::RandomizerWindow._build_ui` | calls=3 called_by=1 callback_refs=0
- `nba2k_editor.ui.randomizer::RandomizerWindow._build_category_tab` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.randomizer::RandomizerWindow._randomize_selected` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.randomizer::RandomizerWindow._default_bounds` | calls=1 called_by=1 callback_refs=0
- `nba2k_editor.ui.randomizer::RandomizerWindow._team_names` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.randomizer::open_randomizer` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.ui.right_click`
- `nba2k_editor.ui.right_click::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ui.stadium_screen`
- `nba2k_editor.ui.stadium_screen::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.stadium_screen::build_stadium_screen` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.stadium_screen::_on_search_changed` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.staff_screen`
- `nba2k_editor.ui.staff_screen::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.staff_screen::build_staff_screen` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.staff_screen::_on_search_changed` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.state.__init__`
- `nba2k_editor.ui.state.__init__::<module>` | calls=0 called_by=0 callback_refs=0

### `nba2k_editor.ui.state.trade_state`
- `nba2k_editor.ui.state.trade_state::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.state.trade_state::TradeSlot.clear` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.state.trade_state::TradeSlot.packages` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.state.trade_state::TradeState.__post_init__` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.state.trade_state::TradeState.current_slot` | calls=0 called_by=3 callback_refs=0
- `nba2k_editor.ui.state.trade_state::TradeState.select_slot` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.state.trade_state::TradeState.clear_slot` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.state.trade_state::TradeState.add_transaction` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.state.trade_state::TradeState.remove_transaction` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.ui.team_shuffle`
- `nba2k_editor.ui.team_shuffle::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.team_shuffle::TeamShuffleWindow.__init__` | calls=1 called_by=4 callback_refs=0
- `nba2k_editor.ui.team_shuffle::TeamShuffleWindow._build_ui` | calls=2 called_by=1 callback_refs=0
- `nba2k_editor.ui.team_shuffle::TeamShuffleWindow._shuffle_selected` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.team_shuffle::TeamShuffleWindow._team_names` | calls=0 called_by=1 callback_refs=0
- `nba2k_editor.ui.team_shuffle::open_team_shuffle` | calls=1 called_by=0 callback_refs=0

### `nba2k_editor.ui.teams_screen`
- `nba2k_editor.ui.teams_screen::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.teams_screen::build_teams_screen` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.teams_screen::_on_search_changed` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.theme`
- `nba2k_editor.ui.theme::<module>` | calls=1 called_by=0 callback_refs=0
- `nba2k_editor.ui.theme::apply_base_theme` | calls=1 called_by=2 callback_refs=0
- `nba2k_editor.ui.theme::_rgb` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.trade_players`
- `nba2k_editor.ui.trade_players::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.trade_players::build_trade_players_screen` | calls=0 called_by=2 callback_refs=0

### `nba2k_editor.ui.widgets`
- `nba2k_editor.ui.widgets::<module>` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.widgets::add_scroll_area` | calls=0 called_by=0 callback_refs=0
- `nba2k_editor.ui.widgets::set_scroll_y` | calls=0 called_by=0 callback_refs=0
